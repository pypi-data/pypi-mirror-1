# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.

import _asterisk

def _swig_setattr(self,class_type,name,value):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    self.__dict__[name] = value

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types



ast_originate = _asterisk.ast_originate

ast_cdr_get_accountcode = _asterisk.ast_cdr_get_accountcode

ast_cdr_get_src = _asterisk.ast_cdr_get_src

ast_cdr_get_dst = _asterisk.ast_cdr_get_dst

ast_cdr_get_dcontext = _asterisk.ast_cdr_get_dcontext

ast_cdr_get_clid = _asterisk.ast_cdr_get_clid

ast_cdr_get_channel = _asterisk.ast_cdr_get_channel

ast_cdr_get_dstchannel = _asterisk.ast_cdr_get_dstchannel

ast_cdr_get_lastapp = _asterisk.ast_cdr_get_lastapp

ast_cdr_get_lastdata = _asterisk.ast_cdr_get_lastdata

ast_cdr_get_start = _asterisk.ast_cdr_get_start

ast_cdr_get_answer = _asterisk.ast_cdr_get_answer

ast_cdr_get_finish = _asterisk.ast_cdr_get_finish

ast_cdr_get_duration = _asterisk.ast_cdr_get_duration

ast_cdr_get_billsec = _asterisk.ast_cdr_get_billsec

ast_cdr_get_disposition = _asterisk.ast_cdr_get_disposition

ast_cdr_get_amaflags = _asterisk.ast_cdr_get_amaflags

ast_cdr_get_uniqueid = _asterisk.ast_cdr_get_uniqueid

ast_cdr_get_userfield = _asterisk.ast_cdr_get_userfield

ast_channel_get_name = _asterisk.ast_channel_get_name

ast_channel_get_language = _asterisk.ast_channel_get_language

ast_channel_get_type = _asterisk.ast_channel_get_type

ast_channel_get_masq = _asterisk.ast_channel_get_masq

ast_channel_get_masqr = _asterisk.ast_channel_get_masqr

ast_channel_get_app = _asterisk.ast_channel_get_app

ast_channel_get_data = _asterisk.ast_channel_get_data

ast_channel_get_dnid = _asterisk.ast_channel_get_dnid

ast_channel_get_callerid = _asterisk.ast_channel_get_callerid

ast_channel_get_ani = _asterisk.ast_channel_get_ani

ast_channel_get_rdnis = _asterisk.ast_channel_get_rdnis

ast_channel_get_context = _asterisk.ast_channel_get_context

ast_channel_get_exten = _asterisk.ast_channel_get_exten

ast_channel_get_priority = _asterisk.ast_channel_get_priority

ast_channel_get_macrocontext = _asterisk.ast_channel_get_macrocontext

ast_channel_get_macroexten = _asterisk.ast_channel_get_macroexten

ast_channel_get_macropriority = _asterisk.ast_channel_get_macropriority

ast_channel_get_cdr = _asterisk.ast_channel_get_cdr

ast_channel_get_uniqueid = _asterisk.ast_channel_get_uniqueid

ast_channel_get_accountcode = _asterisk.ast_channel_get_accountcode

ast_lock_channel = _asterisk.ast_lock_channel

ast_unlock_channel = _asterisk.ast_unlock_channel

ast_channel_byname_locked = _asterisk.ast_channel_byname_locked

ast_channel_byname = _asterisk.ast_channel_byname

ast_channel_keys = _asterisk.ast_channel_keys

ast_verbose = _asterisk.ast_verbose

pbx_findapp = _asterisk.pbx_findapp

ast_softhangup = _asterisk.ast_softhangup

pbx_builtin_getvar_helper = _asterisk.pbx_builtin_getvar_helper

pbx_builtin_setvar_helper = _asterisk.pbx_builtin_setvar_helper

ast_func_write = _asterisk.ast_func_write

reload = _asterisk.reload

ast_db_setitem = _asterisk.ast_db_setitem

ast_db_getitem = _asterisk.ast_db_getitem

ast_exec = _asterisk.ast_exec

ast_func_readp = _asterisk.ast_func_readp

