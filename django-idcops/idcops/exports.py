# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import xlwt
from io import BytesIO

from django.http import HttpResponse
from django.utils import formats, timezone
from django.utils.http import urlquote
from django.utils.text import slugify
from django.utils.encoding import force_text
from django.contrib.admin.utils import label_for_field
from idcops.lib.utils import fields_for_model, display_for_field


def make_to_excel(object_list, fields=None):
    '''
    object_list queryset.
    fields is a list.eg: fields=['id', 'created', 'creator']
    '''
    if not object_list:
        return
    ''' xlwt设置表格的一些样式 '''
    body_style = xlwt.XFStyle()
    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    font = xlwt.Font()
    font.bold = True
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 22
    title_style = xlwt.XFStyle()
    title_style.borders = borders
    title_style.font = font
    title_style.pattern = pattern
    body_style = xlwt.XFStyle()
    body_style.borders = borders
    ''' 开始制作Excel表格 '''
    verbose_name = object_list.model._meta.verbose_name
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('{0}列表'.format(verbose_name))
    model = object_list.model
    fields = fields_for_model(model, fields=fields)
    # 上面 `fields` 获取某个 model fields 列表.
    field_names = []
    field_verboses = []
    for attname, field in fields.items():
        if attname not in ['password']:
            field_names.append(attname)
            field_verboses.append(label_for_field(attname, model))
    for col in range(len(field_verboses)):
        ws.write(0, col, force_text(field_verboses[col]), title_style)
    row = 1
    for obj in object_list:
        for index, field_name in enumerate(field_names):
            field = model._meta.get_field(field_name)
            value = field.value_from_object(obj)
            cell_value = display_for_field(
                value, field, html=False, only_date=False)
            ws.write(row, index, cell_value, body_style)
        row += 1
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    time = formats.localize(
        timezone.template_localtime(timezone.datetime.now())
    )
    filename = urlquote(
        '{}{}'.format(verbose_name, slugify(time, allow_unicode=True))
    )
    # 上面 `filename` 解决导出中文文件名出错的问题
    response = HttpResponse(output)
    # response = StreamingHttpResponse(output)
    # Stream在这里其实是不起作用了,可以直接HttpResponse
    response['charset'] = 'utf-8'
    response['content_type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename="{}.xls"'.format(
        filename)
    return response
