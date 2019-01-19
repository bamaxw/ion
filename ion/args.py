from typing import Dict, Optional, Iterable, List, Any
from dataclasses import dataclass
from copy import copy
import logging
import sys
import __main__

from ion.bash import colors
from ion.decorators import aslist

logger = logging.getLogger(__name__)

# TODO: Write documentation


@dataclass
class ArgSpec:
    name: str
    short: Optional[str] = None
    long: Optional[str] = None
    index: Optional[int] = None
    type: type = str
    default: Optional[Any] = None
    required: bool = True
    provided: bool = False
    flag: bool = False
    named: bool = True
    values: Optional[Iterable] = None
    description: str = ''


class ArgParser(object):
    def __init__(self, script_name: Optional[str] = None, starts_at: int = 0) -> None:
        self.cmd_name = script_name or sys.argv[0]
        self.args: List[str] = sys.argv[starts_at+1:]
        self.arg_specs: Dict[str, ArgSpec] = {}
        self.arg_vals: Dict[str, Any] = {}
        self.list_arg_specs: List[ArgSpec] = []
        self.list_arg_vals: List[Any] = []
        self.starts_at: int = starts_at
        self.current_i: int = 0

    def register(self, key: str, named=True, **config) -> Any:
        if not named:
            return self.register_unnamed(key, **config)
        else:
            return self.register_named(key, **config)

    def register_named(self, key: str, **config) -> Any:
        if 'short' not in config:
            config['short'] = f'-{key[0]}'
        if 'long' not in config:
            config['long'] = f'--{key}'
        if 'default' in config:
            config['required'] = False
        arg_spec = self.arg_specs[key] = ArgSpec(name=key, **config)
        if arg_spec.flag:
            arg_spec.type = bool
        val = self.arg_vals[key] = self._parse_arg(key, arg_spec)
        return val

    def register_unnamed(self, key, **config) -> Any:
        index = self.current_i
        self.current_i += 1
        arg_spec = ArgSpec(**config, name=key, index=index, named=False)
        self.list_arg_specs.append(arg_spec)
        val = self._parse_arg(key, arg_spec)
        self.list_arg_vals.append(val)
        return val

    def validate(self) -> None:
        try:
            for spec in self.list_arg_specs:
                val = self.list_arg_vals[spec.index]
                if not spec.provided:
                    raise ValueError(f'No {spec.name} provided!')
                if type(val) is not spec.type:
                    raise ValueError(f'Type of {spec.name} must be {spec.type.__name__}')
                if spec.values is not None and val not in spec.values:
                    raise ValueError(f'{spec.name} must be one of {spec.values}')
            for key, spec in self.arg_specs.items():
                val = self.arg_vals[key]
                if not spec.provided and spec.required and not spec.flag:
                    raise ValueError(f'Expected {spec.short} or {spec.long} but no found!')
                if type(val) is not spec.type:
                    raise ValueError(f'Type of {key} must be {spec.type.__name__}')
                if spec.values is not None and val not in spec.values:
                    raise ValueError(f'{key} must be one of {spec.values}')
        except ValueError as e:
            logger.error(colors.red + str(e) + colors.reset)
            logger.error(self.print_help())
            raise SystemExit(1)

    def print_help(self) -> str:
        main_msg = f'Usage: {self.cmd_name or __main__.__file__}'
        sub_msgs = []
        for spec in self.list_arg_specs:
            main_msg += f' <{spec.name}>'
            sub_msgs.append(f'\t{spec.name}: {spec.type.__name__}\t{spec.description}')
        for key, spec in self.arg_specs.items():
            if spec.required and not spec.flag:
                main_msg += f' {spec.short}/{spec.long} {key}'
                sub_msgs.append(f'\t{spec.short} / {spec.long}\t\t{key}: {spec.type.__name__}\tREQUIRED')
            elif spec.flag:
                main_msg += f' [{spec.short}/{spec.long}]'
                sub_msgs.append(f'\t{spec.short} / {spec.long}\t\t{key}\tflag')
            else:
                main_msg += f' [{spec.short}/{spec.long} {key}]'
                sub_msgs.append(f'\t{spec.short} / {spec.long}\t\t{key}: {spec.type.__name__}\tdefault: {spec.default}')
        return main_msg + '\n' + '\n'.join(sub_msgs)

    def print_args(self) -> None:
        '''Print all the registered arguments together with their values'''
        for arg, value in self.arg_vals.items():
            print(arg, value)

    def _parse_arg(self, key: str, arg_spec: ArgSpec) -> Any:
        arg_list = self.args
        if not arg_spec.named:
            try:
                value = arg_list[arg_spec.index]
                arg_spec.provided = True
                return value
            except:
                return None
        if arg_spec.long in arg_list:
            arg_spec.provided = True
            if arg_spec.flag:
                return True
            return arg_list[arg_list.index(arg_spec.long) + 1]
        elif arg_spec.short in arg_list:
            arg_spec.provided = True
            if arg_spec.flag:
                return True
            return arg_list[arg_list.index(arg_spec.short) + 1]
        else:
            if arg_spec.flag:
                return False
            return arg_spec.default
