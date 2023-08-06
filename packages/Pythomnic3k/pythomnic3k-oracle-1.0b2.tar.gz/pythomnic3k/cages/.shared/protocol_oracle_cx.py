#!/usr/bin/env python
#-*- coding: iso-8859-1 -*-
################################################################################
#
# This module implements resource to access Oracle databases,
# uses cx_Oracle library.
#
# Sample configuration (config_resource_oracle_1.py)
#
# config = dict \
# (
# protocol = "oracle_cx",                     # meta
# decimal_precision = (10, 2),                # sql
# server_address = ("db.domain.com", 1521),   # oracle
# database = "database",                      # oracle
# username = "user",                          # oracle
# password = "pass",                          # oracle
# )
#
# Sample usage (anywhere):
#
# xa = pmnc.transaction.create()
# xa.oracle_1.execute("INSERT INTO t (id, name) VALUES ({id}, {name})", # query 1
#                     "SELECT name FROM t WHERE id = {id}",             # query 2
#                     id = 123, name = "foo")                           # parameters
# insert_result, select_result = xa.execute()[0]
# assert insert_result == []
# assert select_result == [{"name": "foo"}]
#
# Pythomnic3k project
# (c) 2005-2009, Dmitry Dvoinikov <dmitry@targeted.org>
# Distributed under BSD license
#
###############################################################################

__all__ = [ "Resource" ]

###############################################################################

import os; from os import urandom, environ
import binascii; from binascii import b2a_hex
import decimal; from decimal import Decimal, localcontext, Inexact, ROUND_HALF_UP
import datetime; from datetime import datetime, timedelta
import cx_Oracle; from cx_Oracle import makedsn, connect, TIMESTAMP, INTERVAL

if __name__ == "__main__": # add pythomnic/lib to sys.path
    import os; import sys
    main_module_dir = os.path.dirname(sys.modules["__main__"].__file__) or os.getcwd()
    sys.path.insert(0, os.path.normpath(os.path.join(main_module_dir, "..", "..", "lib")))

import exc_string; from exc_string import exc_string
import typecheck; from typecheck import typecheck
import pmnc.resource_pool; from pmnc.resource_pool import SQLResource

###############################################################################

environ["NLS_LANG"] = "AMERICAN_AMERICA.UTF8"

###############################################################################

class Resource(SQLResource): # Oracle resource

    @typecheck
    def __init__(self, name: str, *,
                 decimal_precision: (int, int),
                 server_address: (str, int),
                 database: str,
                 username: str,
                 password: str):

        SQLResource.__init__(self, name, decimal_precision = decimal_precision)
        precision, scale = decimal_precision
        self.__rounding_decimal_ref = Decimal("1.0") / Decimal(10 ** (scale * 2 + 2))

        self._server_host, self._server_port = server_address
        self._database = database
        self._username = username
        self._password = password

        self._random_separator = "|{0:s}|".format(b2a_hex(urandom(8)).decode("ascii"))

    ###################################

    def __str__(self):
        return "oracle://{0:s}@{1:s}:{2:d}/{3:s}".\
               format(self._username, self._server_host, self._server_port, self._database)

    ###################################

    # this method takes "SELECT {foo} FROM {bar}", { "foo": 1, "bar": 2, "biz": "baz" }
    # and returns "SELECT :foo FROM :bar", { "foo": 1, "bar": 2 }

    def _convert_to_named(self, sql, params):
        sql = sql.format(**{ n: "{0:s}{1:s}{0:s}".format(self._random_separator, n)
                             for n in params.keys() })
        sql_parts = sql.split(self._random_separator)
        return "".join(i % 2 == 1 and ":{0:s}".format(s) or s for i, s in enumerate(sql_parts)), \
               { n: params[n] for n in sql_parts[1::2] }

    ###################################

    def _execute_sql(self, sql, **params):

        pmnc.log.info("{0:s} >> {1:s}".format(self, sql))
        try:

            sql, params = self._convert_to_named(sql, params)

            param_list = ", ".join(map(lambda n_v: "{0:s} = {1:s}".\
                                       format(n_v[0], isinstance(n_v[1], str) and
                                                      "'{0:s}'".format(n_v[1]) or str(n_v[1])),
                                       params.items()))
            pmnc.log.debug("{0:s} -- {1:s} -- ({2:s})".format(self, sql, param_list))

            cursor = self._connection.cursor()
            try:

                # avoid truncation of timestamps and intervals

                param_sizes = {}
                for n, v in params.items():
                    if isinstance(v, datetime):
                        param_sizes[n] = TIMESTAMP
                    elif isinstance(v, timedelta):
                        param_sizes[n] = INTERVAL
                if param_sizes:
                    cursor.setinputsizes(**param_sizes)

                # execute the query

                cursor.execute(sql, **params)

                # extract the result

                if cursor.description is not None:
                    description = tuple(dict(name = t[0], type_name = t[1].__name__) for t in cursor.description)
                    records = [ { field["name"]: self.cx_TYPE(field["type_name"], value)
                                  for field, value in zip(description, record) } for record in cursor ]
                else:
                    records = [] # not a SELECT query

                records_affected = cursor.rowcount

            finally:
                cursor.close()

        except:
            pmnc.log.error("{0:s} << {1:s}".format(self, exc_string()))
            raise
        else:
            pmnc.log.info("{0:s} << OK{1:s}".format(self, records_affected >= 0 and
                          ", {0:d} record(s)".format(records_affected) or ""))
            return records

    ###################################

    _supported_types = SQLResource._supported_types | { float, timedelta } - { bool }

    def _py_to_sql_float(self, v):
        return v

    def _sql_to_py_float(self, v):
        return v

    def _py_to_sql_timedelta(self, v):
        return v

    def _sql_to_py_timedelta(self, v):
        return v

    ###################################

    class cx_TYPE:
        def __init__(self, type_name, value):
            self.type_name, self.value = type_name, value

    def _sql_to_py_cx_TYPE(self, v):
        return getattr(self, "_cx_to_py_{0:s}".format(v.type_name))(v.value)

    def _cx_to_py_STRING(self, v):
        if v is None:
            return None
        return str(v)

    _cx_to_py_FIXED_CHAR = _cx_to_py_LONG_STRING = \
    _cx_to_py_CLOB = _cx_to_py_NCLOB = _cx_to_py_STRING

    def _cx_to_py_NUMBER(self, v): # whose idea was it to return fixed precision NUMBER's as float's ?!

        if v is None:
            return None
        elif isinstance(v, int):
            return v

        # step 1 - recover the decimal corresponding as close as possible to the provided float

        n, d = map(Decimal, v.as_integer_ratio())
        with localcontext() as ctx:
            ctx.prec = 8
            ctx.traps[Inexact] = True
            while True:
                try:
                    result = ctx.divide(n, d)
                except Inexact:
                    ctx.prec *= 2
                else:
                    break

        # step 2 - apply some pessimistic rounding hoping the result will be in range

        with localcontext() as ctx:
            ctx.traps[Inexact] = False
            result = result.quantize(self.__rounding_decimal_ref, rounding = ROUND_HALF_UP)

        # step 3 - check that the result is in range and return it cut down to the precision

        self._ensure_decimal_in_range(result)
        return result.quantize(self._SQLResource__decimal_ref)

    def _cx_to_py_NATIVE_FLOAT(self, v):
        return v

    def _cx_to_py_BINARY(self, v):
        return v

    _cx_to_py_LONG_BINARY = _cx_to_py_BINARY

    def _cx_to_py_BLOB(self, v):
        if v is None:
            return None
        return v.read()

    def _cx_to_py_ROWID(self, v):
        return v

    def _cx_to_py_DATETIME(self, v):
        return v

    _cx_to_py_TIMESTAMP = _cx_to_py_DATETIME

    def _cx_to_py_INTERVAL(self, v):
        return v

    ###################################

    def connect(self):
        dsn = makedsn(self._server_host, self._server_port, self._database)
        self._connection = connect(user = self._username, password = self._password,
                                   dsn = dsn, threaded = 1) # 1 = OCI_THREADED
        try:
            self._connection.autocommit = False
        except:
            self._connection.close()
            raise
        SQLResource.connect(self)

    def begin_transaction(self, *args, **kwargs):
        SQLResource.begin_transaction(self, *args, **kwargs)
        self._connection.begin()

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def disconnect(self):
        try:
            self._connection.close()
        except:
            pmnc.log.error(exc_string()) # log and ignore
        SQLResource.disconnect(self)

###############################################################################

def self_test():

    from expected import expected
    from pmnc.request import fake_request
    from math import log10
    from cx_Oracle import DatabaseError

    ###################################

    rus = "\u0410\u0411\u0412\u0413\u0414\u0415\u0401\u0416\u0417\u0418\u0419" \
          "\u041a\u041b\u041c\u041d\u041e\u041f\u0420\u0421\u0422\u0423\u0424" \
          "\u0425\u0426\u0427\u0428\u0429\u042c\u042b\u042a\u042d\u042e\u042f" \
          "\u0430\u0431\u0432\u0433\u0434\u0435\u0451\u0436\u0437\u0438\u0439" \
          "\u043a\u043b\u043c\u043d\u043e\u043f\u0440\u0441\u0442\u0443\u0444" \
          "\u0445\u0446\u0447\u0448\u0449\u044c\u044b\u044a\u044d\u044e\u044f"

    random_string = lambda n: b2a_hex(urandom(n))[:n].decode("ascii")

    ###################################

    def test_convert_to_named():

        db_config = pmnc.config_resource_oracle_1.copy()
        assert db_config.pop("protocol") == "oracle_cx"
        r = Resource("test", **db_config)

        assert r._convert_to_named("", {}) == ("", {})
        assert r._convert_to_named("", { "foo": 1 }) == ("", {})
        assert r._convert_to_named("{foo}", { "foo": 1 }) == (":foo", { "foo": 1 })
        with expected(KeyError("foo")):
            r._convert_to_named("{foo}", {})

        assert r._convert_to_named("{{{foo}}}", { "foo": 1, "bar": 2 }) == ("{:foo}", { "foo": 1 })
        assert r._convert_to_named("{foo}{foo}", { "foo": 1 }) == (":foo:foo", { "foo": 1 })
        assert r._convert_to_named("{foo}:foo:{{foo}}:foo{foo}", { "foo": 1 }) == (":foo:foo:{foo}:foo:foo", { "foo": 1 })
        with expected(KeyError("foo{{foo}}")):
            r._convert_to_named("{{{foo{{foo}}}}}", { "foo": 1 })
        assert r._convert_to_named("{{{foo}{{{foo}}}}}", { "foo": 1, "bar": None }) == ("{:foo{:foo}}", { "foo": 1 })

        assert r._convert_to_named("SELECT {foo} FROM {bar}", { "foo": 1, "bar": 2, "biz": "baz" }) == \
               ("SELECT :foo FROM :bar", { "foo": 1, "bar": 2 })

    test_convert_to_named()

    ###################################

    def test_session_params():

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("SELECT VALUE FROM NLS_SESSION_PARAMETERS WHERE PARAMETER = 'NLS_NUMERIC_CHARACTERS'")
        record = xa.execute()[0][0][0]
        assert record["VALUE"][0] == record["value"][0] == "." # this is required, set NLS_LANG properly

    test_session_params()

    ###################################

    def test_transaction_isolation():

        fake_request(10.0)

        tn = "table_{0:s}".format(random_string(8))

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("CREATE TABLE {0:s} (ID NUMBER(8) NOT NULL PRIMARY KEY)".format(tn))
        xa.execute()

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("INSERT INTO {0:s} (ID) VALUES ({{id}})".format(tn),
                            "SELECT ID FROM {0:s}".format(tn), id = 1)
        xa.oracle_1.execute("INSERT INTO {0:s} (ID) VALUES ({{id}})".format(tn),
                            "SELECT ID FROM {0:s}".format(tn), id = 2)
        assert xa.execute() == (([], [{ "ID": 1 }]), ([], [{ "ID": 2 }]))

        fake_request(5.0)

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("INSERT INTO {0:s} (ID) VALUES ({{id}})".format(tn), id = 3) # causes a deadlock
        xa.oracle_1.execute("INSERT INTO {0:s} (ID) VALUES ({{id}})".format(tn), id = 3)
        with expected(Exception("request deadline")):
            xa.execute()

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("SELECT id FROM {0:s} ORDER BY id".format(tn),
                            "DROP TABLE {0:s}".format(tn))
        assert xa.execute()[0] == ([{ "ID": 1 }, { "ID": 2 }], [])

    test_transaction_isolation()

    ###################################

    def test_ddl_transactions():

        def test_sequential():

            fake_request(10.0)

            tn = "table_{0:s}".format(random_string(8))

            xa = pmnc.transaction.create()
            xa.oracle_1.execute("CREATE TABLE {0:s} (ID NUMBER(8))".format(tn),
                                "INSERT INTO {0:s} (ID) VALUES ({{id}})".format(tn),
                                "THIS SHOULD FAIL", id = 1)
            with expected(DatabaseError("ORA-00900")):
                xa.execute()

            # because in Oracle DDL commits, the empty table remains

            xa = pmnc.transaction.create()
            xa.oracle_1.execute("SELECT COUNT(*) AS c FROM {0:s}".format(tn),
                                "DROP TABLE {0:s}".format(tn))
            assert xa.execute()[0][0][0]["c"] == 0

            # see if data inserted before the DDL stays

            tn1 = "table_{0:s}".format(random_string(8))
            tn2 = "table_{0:s}".format(random_string(8))

            xa = pmnc.transaction.create()
            xa.oracle_1.execute("CREATE TABLE {0:s} (ID NUMBER(8))".format(tn1),
                                "INSERT INTO {0:s} (ID) VALUES ({{id}})".format(tn1),
                                "CREATE TABLE {0:s} (ID NUMBER(8))".format(tn2),
                                "INSERT INTO {0:s} (ID) VALUES ({{id}})".format(tn2),
                                "THIS SHOULD FAIL", id = 1)
            with expected(DatabaseError("ORA-00900")):
                xa.execute()

            xa = pmnc.transaction.create()
            xa.oracle_1.execute("SELECT COUNT(*) AS c FROM {0:s}".format(tn1),
                                "DROP TABLE {0:s}".format(tn1),
                                "SELECT COUNT(*) AS c FROM {0:s}".format(tn2),
                                "DROP TABLE {0:s}".format(tn2))
            assert xa.execute()[0] == ([{ "C": 1 }], [], [{ "C": 0 }], [])

        test_sequential()

        def test_parallel():

            tn1 = "table_{0:s}".format(random_string(8))
            tn2 = "table_{0:s}".format(random_string(8))

            # when executed in separate connections, the transactions only commit up to the DDL

            xa = pmnc.transaction.create()
            xa.oracle_1.execute("CREATE TABLE {0:s} (ID NUMBER(8))".format(tn1),
                                "INSERT INTO {0:s} (ID) VALUES ({{id}})".format(tn1), id = 1)
            xa.oracle_1.execute("CREATE TABLE {0:s} (ID NUMBER(8))".format(tn2),
                                "INSERT INTO {0:s} (ID) VALUES ({{id}})".format(tn2), id = 2)
            xa.oracle_1.execute("THIS SHOULD FAIL")
            with expected(DatabaseError("ORA-00900")):
                xa.execute()

            xa = pmnc.transaction.create()
            xa.oracle_1.execute("SELECT COUNT(*) AS c FROM {0:s}".format(tn1),
                                "DROP TABLE {0:s}".format(tn1),
                                "SELECT COUNT(*) AS c FROM {0:s}".format(tn2),
                                "DROP TABLE {0:s}".format(tn2))
            assert xa.execute()[0] == ([{ "C": 0 }], [], [{ "C": 0 }], [])

        test_parallel()

    test_ddl_transactions()

    ###################################

    def test_data_types():

        def test_data_type(t, vs):

            tn = "table_{0:s}".format(random_string(8))

            sqls = [ "CREATE TABLE {0:s} (i number(8), v {1:s})".format(tn, t) ]
            params = {}
            for i, v in enumerate(vs):
                sqls.append("INSERT INTO {0:s} (i, v) VALUES ({1:d}, {{v{1:d}}})".format(tn, i))
                params["v{0:d}".format(i)] = v
            sqls.append("SELECT v FROM {0:s} ORDER BY i".format(tn))
            sqls.append("DROP TABLE {0:s}".format(tn))

            fake_request(10.0)

            xa = pmnc.transaction.create()
            xa.oracle_1.execute(*sqls, **params)
            records = xa.execute()[0][-2]
            result = [ r["V"] for r in records ] # note that field name is capitalized
            return result

        # char

        assert test_data_type("char", [ None, "", "1" ]) == [ None, None, "1" ]
        assert test_data_type("char(2)", [ "1" ]) == [ "1 " ]
        with expected(DatabaseError("ORA-12899")): # value too large for column
            test_data_type("char(1)", [ rus[0] ])
        with expected(DatabaseError("ORA-00910")): # specified length too long for its datatype
            test_data_type("char(10000)", [])

        # nchar

        assert test_data_type("nchar", [ None, "", "1", rus[0] ]) == [ None, None, "1", rus[0] ]
        assert test_data_type("nchar(2)", [ "1" ]) == [ "1 " ]
        assert test_data_type("nchar(66)", [ rus ]) == [ rus ]
        with expected(DatabaseError("ORA-12899")): # value too large for column
            test_data_type("nchar(1)", [ rus[0:2] ])
        with expected(DatabaseError("ORA-00910")): # specified length too long for its datatype
            test_data_type("nchar(10000)", [])

        # varchar2

        assert test_data_type("varchar2(1)", [ None, "", "1" ]) == [ None, None, "1" ]
        assert test_data_type("varchar2(2)", [ "1" ]) == [ "1" ]
        with expected(DatabaseError("ORA-12899")): # value too large for column
            test_data_type("varchar2(1)", [ rus[0] ])
        with expected(DatabaseError("ORA-00910")): # specified length too long for its datatype
            test_data_type("varchar2(10000)", [])

        # nvarchar2

        assert test_data_type("nvarchar2(1)", [ None, "", "1", rus[0] ]) == [ None, None, "1", rus[0] ]
        assert test_data_type("nvarchar2(2)", [ "1" ]) == [ "1" ]
        assert test_data_type("nvarchar2(66)", [ rus ]) == [ rus ]
        with expected(DatabaseError("ORA-12899")): # value too large for column
            test_data_type("nvarchar2(1)", [ rus[0:2] ])
        with expected(DatabaseError("ORA-00910")): # specified length too long for its datatype
            test_data_type("nvarchar2(10000)", [])

        # long

        assert test_data_type("long", [ None, "", "x" * 10000 ]) == [ None, None, "x" * 10000 ]

        # clob

        assert test_data_type("clob", [ None, "", "x" * 10000 ]) == [ None, None, "x" * 10000 ]

        # nclob

        assert test_data_type("nclob", [ None, "", rus * 150 ]) == [ None, None, rus * 150 ]

        # number

        assert test_data_type("number(2)", [ None, 0, 99, -99, Decimal("0"), Decimal("99"), Decimal("-99"), 0.0, 99.0, -99.0 ]) == \
               [ None, 0, 99, -99, 0, 99, -99, 0, 99, -99 ]
        assert test_data_type("number(2)", [ Decimal("98.99"), Decimal("-98.99"), 98.99, -98.99 ]) == [ 99, -99, 99, -99 ]
        with expected(DatabaseError("ORA-01722")): # invalid number
            test_data_type("number(2)", [ "x" ])
        with expected(DatabaseError("ORA-01438")): # value larger than specified precision allowed for this column
            test_data_type("number(2)", [ 100 ])
        assert test_data_type("number(2)", [ Decimal("0.1") ]) == [ 0 ]
        assert test_data_type("number(2)", [ 0.1 ]) == [ 0 ]

        assert test_data_type("number(4, 2)", [ None, 0, 99, -99, Decimal("0.0"), Decimal("99.99"), Decimal("-99.99"), Decimal("0.01"), Decimal("-0.01"), 0.0, 99.99, -99.99, 0.01, -0.01 ]) == \
               [ None, Decimal("0.00"), Decimal("99.00"), Decimal("-99.00"), Decimal("0.00"), Decimal("99.99"), Decimal("-99.99"), Decimal("0.01"), Decimal("-0.01"), Decimal("0.00"), Decimal("99.99"), Decimal("-99.99"), Decimal("0.01"), Decimal("-0.01") ]
        assert test_data_type("number(4, 2)", [ Decimal("0.0001"), Decimal("-99.9899"), Decimal("99.9899") ]) == \
               [ Decimal("0.00"), Decimal("-99.9900"), Decimal("99.9900") ]
        with expected(DatabaseError("ORA-01722")): # invalid number
            test_data_type("number(4, 2)", [ "0,0" ])
        with expected(DatabaseError("ORA-01438")): # value larger than specified precision allowed for this column
            test_data_type("number(4, 2)", [ Decimal("100.00") ])

        assert test_data_type("number(7, 4)", [ None, 999, -999, Decimal("999.9999"), Decimal("-999.9999"), Decimal("0.0001"), Decimal("-0.0001"), 999.9999, -999.9999, 0.0001, -0.0001 ]) == \
               [ None, Decimal("999.0000"), Decimal("-999.0000"), Decimal("999.9999"), Decimal("-999.9999"), Decimal("0.0001"), Decimal("-0.0001"), Decimal("999.9999"), Decimal("-999.9999"), Decimal("0.0001"), Decimal("-0.0001") ]
        with expected(DatabaseError("ORA-01438")): # value larger than specified precision allowed for this column
            test_data_type("number(7, 4)", [ 1000 ])
        with expected(DatabaseError("ORA-01438")): # value larger than specified precision allowed for this column
            test_data_type("number(7, 4)", [ 1000.0 ])
        with expected(ValueError("decimal value too precise")):
            test_data_type("number(7, 4)", [ Decimal("0.00001") ]) # decimal is precision-controlled
        test_data_type("number(7, 4)", [ 0.00001 ]) # while float is not

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("SELECT 0.1 AS X1, 0.01 AS X2, 0.001 AS X3, 0.0001 AS X4 FROM dual")
        assert xa.execute()[0][0] == [ dict(X1 = Decimal("0.1"), X2 = Decimal("0.01"), X3 = Decimal("0.001"), X4 = Decimal("0.0001")) ]

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("SELECT 0.00001 AS X5 FROM dual")
        with expected(ValueError("decimal value too precise")):
            xa.execute()

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("SELECT 0.0000999999 AS X4 FROM dual") # not enough nines to be considered exact
        with expected(ValueError("decimal value too precise")):
            xa.execute()

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("SELECT 0.00009999999 AS X4 FROM dual") # enough nines to be considered exact
        assert xa.execute()[0][0] == [ dict(X4 = Decimal("0.0001")) ]

        # float

        def loose_compare(a, b):
            assert len(a) == len(b)
            for aa, bb in zip(a, b):
                if (aa is None and bb is None) or (aa == float("nan") and bb == float("nan")) or \
                   (aa == float("inf") and bb == float("inf")) or (aa == float("-inf") and bb == float("-inf")):
                    continue
                if abs(aa) < 1e-6 and abs(bb) < 1e-6:
                    continue
                if (aa < 0.0 and bb >= 0.0) or (bb < 0.0 and aa >= 0.0):
                    return False
                if abs(log10(abs(aa)) - log10(abs(bb))) > 1e-6:
                    return False
            else:
                return True

        assert loose_compare(test_data_type("binary_float", [ None, 0, 1000000, -1000000, Decimal("0.0"), Decimal("999.9999"), Decimal("-999.9999"), 0.0, 1000.0, -1000.0 ]),
                             [None, 0.0, 1000000.0, -1000000.0, 0.0, 1000.0, -1000.0, 0.0, 1000.0, -1000.0])

        assert loose_compare(test_data_type("binary_float", [ -3.5e+38, -3.4e+38, 3.4e+38, 3.5e+38 ]),
                             [ float("-inf"), -3.40e+38, 3.40e+38, float("inf") ])

        assert loose_compare(test_data_type("binary_double", [ None, 0, 1000000, -1000000, Decimal("0.0"), Decimal("999.9999"), Decimal("-999.9999"), 0.0, 1000.0, -1000.0 ]),
                             [None, 0.0, 1000000.0, -1000000.0, 0.0, 1000.0, -1000.0, 0.0, 1000.0, -1000.0])

        assert loose_compare(test_data_type("binary_double", [ -1e+126, -1e+125, 1e+125, 1e+126 ]),
                             [ float("-inf"), -1e+125, 1e+125, float("inf") ])

        # binary

        assert test_data_type("raw(1)", [ None, b"", b"\x00" ]) == [ None, None, b"\x00" ]
        assert test_data_type("raw(2000)", [ b"\xff" * 2000 ]) == [ b"\xff" * 2000 ]
        with expected(DatabaseError("ORA-00910")): # specified length too long for its datatype
            test_data_type("raw(10000)", [])

        test_data_type("blob", [ None, b"", b"\x00" ]) == [ None, b"", b"\x00" ]
        assert test_data_type("blob", [ b"\xff" * 10000 ]) == [ b"\xff" * 10000 ]

        test_data_type("long raw", [ None, b"", b"\x00" ])
        assert test_data_type("long raw", [ b"\xff" * 10000 ]) == [ b"\xff" * 10000 ]

        # rowid

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("SELECT rowid AS RID, ROWIDTOCHAR(rowid) AS RIDC FROM dual")
        r = xa.execute()[0][0][0]
        assert r["RID"] == r["RIDC"]

        # date

        test_data_type("date", [ None, datetime(2009, 12, 31), datetime(2009, 12, 31, 23, 59, 59), datetime(2009, 12, 31, 23, 59, 59, 999999) ]) == \
                               [ None, datetime(2009, 12, 31), datetime(2009, 12, 31, 23, 59, 59), datetime(2009, 12, 31, 23, 59, 59) ]

        # timestamp

        assert test_data_type("timestamp", [ None, datetime(2009, 12, 31), datetime(2009, 12, 31, 23, 59, 59), datetime(2009, 12, 31, 23, 59, 59, 999999) ]) == \
               [ None, datetime(2009, 12, 31), datetime(2009, 12, 31, 23, 59, 59), datetime(2009, 12, 31, 23, 59, 59, 999999) ]

        assert test_data_type("timestamp(3)", [ None, datetime(2009, 12, 31), datetime(2009, 12, 31, 23, 59, 59), datetime(2009, 12, 31, 23, 59, 59, 123456) ]) == \
               [ None, datetime(2009, 12, 31), datetime(2009, 12, 31, 23, 59, 59), datetime(2009, 12, 31, 23, 59, 59, 123000) ]

        # interval (day to second)

        assert test_data_type("interval day to second", [ None, timedelta(seconds = 1) ]) == [ None, timedelta(seconds = 1) ]

    test_data_types()

    ###################################

    def test_pl_sql():

        pn = "proc_{0:s}".format(random_string(8))

        fake_request(10.0)

        xa = pmnc.transaction.create()
        xa.oracle_1.execute("""
CREATE OR REPLACE FUNCTION {0:s} (I NUMBER) RETURN NUMBER IS
BEGIN
    RETURN I * I;
END;
""".format(pn),
                            "SELECT {0:s}(10) AS RESULT FROM dual".format(pn),
                            "DROP FUNCTION {0:s}".format(pn))
        assert xa.execute()[0] == ([], [ { "RESULT": 100 } ], [])

    test_pl_sql()

    ###################################

if __name__ == "__main__": import pmnc.self_test; pmnc.self_test.run()

###############################################################################
# EOF