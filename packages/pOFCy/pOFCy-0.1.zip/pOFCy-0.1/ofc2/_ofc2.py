#!/usr/bin/env python
# encoding: utf-8

__all__ = []
number = (int, float)
array = (list, tuple)

class OFCBase(dict):
    accept = ()
    defaults = {}
    replace = {
        'font_size':'font-size', 'fontsize': 'font-size',
        'color':'colour', 'bg_color':'bg_colour', 'bgcolor':'bg_colour',
        'dot_size': 'dot-size', 'dotsize':'dot-size', 'tooltip': 'tip',
        'grid_colour': 'grid-colour', 'grid_color': 'grid-colour',
        'tick_length': 'tick-length', 'tick_height': 'tick-height',
        'on_click':'on-click', 'outline_color':'outline-colour',
        'outline_colour':'outline-colour', 'fill_color':'fill',
        'fill_colour':'fill', 'fill_alpha':'fill-alpha',
        'halo_size':'halo-size', 'halosize':'halo-size','no_labels':'no-labels',
        'dotstyle': 'dot-style', 'dot_style': 'dot-style',
        'proximity': 'mouse', 'spoke_labels':'spoke-labels',
        'visible_steps': 'visible-steps', 'visiblesteps': 'visible-steps',
        'gradient_fill': 'gradient-fill'
        }
    predefinedtypes = {
        "alpha": float, "bottom": int, "axis": str, "colour": str,
        "dot-size": number,
        "fill": str, "fill-alpha": float, "font-size": int, "grid-colour": str,
        "halo-size": number, "label-colour": str, "loop": bool, "max": number,
        "min": number, "offset": int, "on-click": str, "outline-colour": str,
        "rotate": number, "rotation": number, "size": number, "steps": number,
        "stroke": number, "style": str, "text": str, "tick-height": number,
        "tick-length": number, "tip": str, "top": int, "type": str,
        "value": number, "values": array, "visible-steps": int,
        "width": number, "x": number, "y": number
        }

    def __setattr__(self, name, value):
        name = self.replace.get(name, name)
        if name in self.accept:
            if name in self.typetable:
                if not isinstance(value, self.typetable[name]):
                    raise TypeError(
                        "invalid type ``%s`` for argument ``%s``" % (
                        type(value).__name__, name))
            self[name] = value
        else:
            raise NameError("`%s` is not acceptable name in %s" % (
                name, self.__class__.__name__))
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __init__(self, **kwargs):
        self.update(copy.deepcopy(self.defaults))
        self.set(**kwargs)

    def set(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        return self

import sys, copy

def istupleoftypes(values):
    return isinstance(values, tuple) and all(
        isinstance(value, type) or istupleoftypes(value) for value in values)

def make(clsname, *args, **defaults):
    names = []
    bases = []
    typetable = dict()
    for arg in args:
        if isinstance(arg, str):
            names.append(arg)
            if arg in OFCBase.predefinedtypes:
                typetable[arg] = OFCBase.predefinedtypes[arg]
        elif isinstance(arg, type) and issubclass(arg, OFCBase):
            bases.append(arg)
        else:
            raise TypeError("invalid argument type %s" % type(arg).__name__)
    temp_defaults = dict()
    for base in bases:
        temp_defaults.update(base.defaults)
        typetable.update(base.typetable)
    bases = (OFCBase,) if not bases else tuple(bases)
    for name, value in list(defaults.items()):
        if isinstance(value, type) or istupleoftypes(value):
            typetable[name] = defaults.pop(name)
    temp_defaults.update(defaults)
    defaults = dict((OFCBase.replace.get(name, name), value)
        for name, value in temp_defaults.items())
    typetable = dict((OFCBase.replace.get(name, name), value)
        for name, value in typetable.items())
    accept = tuple(set(sum((base.accept for base in bases),
        tuple(names+list(defaults.keys())+list(typetable.keys())))))
    for name, value in list(defaults.items()):
        if name in typetable:
            if not isinstance(value, typetable[name]):
                raise TypeError('type conflict for ``%s``' % name)
        else:
            typetable[name] = type(value)

    cls = type(clsname, bases, dict(
        accept=accept, defaults=defaults, typetable=typetable))
    scope = sys._getframe(1).f_locals
    scope[clsname] = cls
    scope['__all__'].append(clsname)
    return cls

make('dot_base', 'type', 'value', 'x', 'y', 'colour', 'tip', 'dot-size',
    'halo-size', 'on-click')

make('hollow_dot', dot_base, type='hollow-dot')
make('star', dot_base, 'rotation', hollow=bool, type='star')
make('bow', dot_base, 'rotation', type='bow')
make('anchor', dot_base, 'rotation', sides=int, type='anchor')
make('dot', dot_base, type='dot')
make('solid_dot', dot_base, type='solid-dot')

make('line_style', on=number, off=number, style="dash")

make('line', 'values', 'width', 'colour', 'dot-size', 'halo-size', 'text',
    'tip', 'on-click', 'loop', 'font-size', line_style=line_style,
    type="line")

make('dot_value', 'value', 'colour', 'size', 'tip')
make('line_dot', line, dot_style=solid_dot())
make('line_hollow', line, dot_style=hollow_dot())

make('area', line, 'fill', 'fill-alpha', type='area')

make('area_hollow', area, dot_style=hollow_dot(), type='area')
make('area_line', area, dot_style=dot(), type='area')

make('bar_value', 'top', 'bottom', 'tip')
make('bar_filled_value', bar_value, 'outline-colour')

make('bar_base', 'text', 'font-size', 'values', 'colour', 'alpha', 'tip',
    'on-show', 'on-click', 'axis')
make('bar', bar_base, type='bar')

make('bar_3d_value', 'top', 'colour', 'tip')

make('bar_filled', bar_base, 'outline-colour', type="bar_filled")
make('bar_cylinder', bar_base, type="bar_cylinder")
make('bar_cylinder_outline', bar_base, type="bar_cylinder_outline")
make('bar_rounded_glass', bar_base, type="bar_round_glass")
make('bar_round', bar_base, type="bar_round")
make('bar_dome', bar_base, type="bar_dome")
make('bar_round3d', bar_base, type="bar_round3d")
make('bar_3d', bar_base, type="bar_3d")
make('bar_sketch', bar_filled, 'offset', type="bar_sketch")

make('bar_stack', bar_base, keys=array, colours=array, type="bar_stack")
make('bar_stack_value', 'colour', 'tip', val=number)
make('bar_stack_key', 'colour', 'text', 'font-size')

make('hbar_value', 'colour', 'tip', left=number, right=number)
make('hbar', 'text', 'font-size', 'tip', 'values', 'colour', type="hbar")

make('base_pie_animation')
make('pie_value', 'value', 'colour', 'label-colour', 'font-size',
    'tip', 'on-click', animate=base_pie_animation, label=str)
make('pie_fade', base_pie_animation, type="fade")
make('pie_bounce', base_pie_animation, 'distance', type="bounce")
make('pie', 'alpha', 'values', 'animate', 'tip', 'label-colour', 'on-click',
    gradient_fill=str, no_labels=bool, colours=array, start_angle=number,
    radius=number, type='pie')

make('radar_axis_labels', 'colour', labels=array)
make('radar_spoke_labels', 'colour', labels=array)
make('radar_axis', 'max', 'steps', 'stroke', 'colour', 'grid-colour',
    spoke_labels=radar_spoke_labels, labels=radar_axis_labels)

make('scatter_value', 'x', 'y', 'tip', 'on-click', 'dot-size')

make('scatter', 'colour', 'dot-size', 'values', dot_style=solid_dot(),
    type='scatter')
make('scatter_line', 'colour', 'width', 'values', 'text', 'dot-size',
    'font-size', stepgraph=str, dot_style=dot_base(type='solid-dot'),
    type="scatter_line")

make('title', 'style', text='')

make('tooltip', 'stroke', 'colour', shadow=bool, background=str,
    title=str, body=str, mouse=int)

make('shape_point', 'x', 'y')
make('shape', 'colour', 'values', type="shape")

make('x_axis_label', 'text', 'colour', 'size', 'rotate', visible=bool)
make('x_axis_labels', 'steps', 'visible-steps', 'colour', 'size', 'rotate',
    'text', labels=array)
make('x_axis', 'stroke', 'colour', 'tick-height', 'grid-colour', 'offset',
    'steps', '3d', 'min', 'max', labels=(x_axis_labels, array))
make('x_legend', 'style', text='')

make('y_axis_label', 'y', 'text', 'colour', 'size', 'rotate')
make('y_axis_labels', 'steps', 'colour', 'size', 'rotate', 'text', labels=array)

make('y_axis_base', 'stroke', 'tick-length', 'colour', 'grid-colour', 'min',
    'max', 'offset', 'rotate', steps=1, labels=(y_axis_labels, array))
make('y_axis', y_axis_base, 'grid-colour')
make('y_axis_right', y_axis_base)
make('y_legend', 'text', 'style')

try:
    import cjson
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        try:
            import json
        except ImpostError:
            raise
    dumper = json.dumps
    def prettydumper(data):
        return json.dumps(data, sort_keys=True, indent=4)
else:
    dumper = cjson.encode
    prettydumper = cjson.encode

make('open_flash_chart', bg_colour=str, tip=tooltip, title=title,
    x_legend=x_legend, y_legend=y_legend, x_axis=x_axis, y_axis=y_axis,
    y_axis_right=y_axis_right, radar_axis=radar_axis, elements=[])

class open_flash_chart(open_flash_chart):
    def add_element(self, element):
        self.elements.append(element)
    __str__ = dumper
    render = prettydumper
