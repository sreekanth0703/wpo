from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from xlrd import open_workbook, xldate_as_datetime
from collections import OrderedDict
from wpo_admin.models import *
from django.db.models import Q
import copy
import re
import json
# Create your views here.

EMPLOYEE_UPLOAD_MAPPING = {'Name': 'name', 'Email': 'email', 'Phone Number': 'phone_number', 'Date of Birth': 'dob'}
DATATABLE_RESPONSE = {"draw": 1, "recordsTotal": 0, "recordsFiltered": 0, "data": []}

def uploads(request):
    return render(request, "templates/uploads.html")

def check_return_excel(fname):
    ''' Check and Return Excel data'''
    status, reader, no_of_rows, no_of_cols, file_type, date_mode = '', '', '', '', '', ''
    if (fname.name).split('.')[-1] == 'csv':
        reader = [[val.replace('\n', '').replace('\t', '').replace('\r', '') for val in row] for row in
                  csv.reader(fname.read().splitlines())]
        no_of_rows = len(reader)
        file_type = 'csv'
        no_of_cols = 0
        if reader:
            no_of_cols = len(reader[0])
    elif (fname.name).split('.')[-1] == 'xls' or (fname.name).split('.')[-1] == 'xlsx':
        try:
            data = fname.read()
            open_book = open_workbook(filename=None, file_contents=data)
            open_sheet = open_book.sheet_by_index(0)
            date_mode = open_book.datemode
        except:
            status = 'Invalid File'
        reader = open_sheet
        no_of_rows = reader.nrows
        file_type = 'xls'
        no_of_cols = open_sheet.ncols
    return reader, no_of_rows, no_of_cols, file_type, status, date_mode


def get_cell_data(row_idx, col_idx, reader='', file_type='xls'):
    ''' Reads Excel cell Data '''
    try:
        if file_type == 'csv':
            cell_data = reader[row_idx][col_idx]
        else:
            cell_data = reader.cell(row_idx, col_idx).value
    except:
        cell_data = ''
    return cell_data

def get_excel_upload_mapping(reader, no_of_rows, no_of_cols, fname, file_type, base_mapping):
    file_mapping = OrderedDict()
    for ind in range(0, no_of_cols):
        cell_data = get_cell_data(0, ind, reader, file_type)
        if cell_data in base_mapping:
            file_mapping[base_mapping[cell_data]] = ind
    return file_mapping


@csrf_exempt
def employee_upload(request):
    fname = request.FILES.get('files-0', '')
    if not fname:
        return HttpResponse("File Not Found")
    extension = fname.name.split('.')[-1]
    if extension not in ['xls', 'csv', 'xlsx']:
        return HttpResponse("Invalid File format")
    reader, no_of_rows, no_of_cols, file_type, status, date_mode = check_return_excel(fname)
    if status:
        return HttpResponse(status)
    emp_mapping = copy.deepcopy(EMPLOYEE_UPLOAD_MAPPING)
    file_mapping = get_excel_upload_mapping(reader, no_of_rows, no_of_cols, fname, file_type, emp_mapping)
    new_employees = []
    for ind in range(1, no_of_rows):
        row_data = OrderedDict()
        for key, value in file_mapping.items():
            cell_data = get_cell_data(ind, value, reader, file_type)
            ignore_data = False
            if key == 'dob':
                if isinstance(cell_data, float):
                    cell_data = xldate_as_datetime(cell_data, date_mode)
                elif '-' in row_data[key]:
                    cell_data = datetime.datetime.strptime(cell_data, '%d-%m-%Y')
                else:
                    ignore_data = True
            elif key == 'phone_number':
                if isinstance(cell_data, float):
                    cell_data = str(int(cell_data))
                if len(cell_data) != 10:
                    ignore_data = True
            elif key == 'email':
                if not re.search('^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', cell_data):
                    ignore_data = True
            row_data[key] = cell_data
        if not ignore_data:
            exist_obj = Employee.objects.filter(name=row_data['name'], email=row_data['email'])
            if not exist_obj.exists():
                new_employees.append(Employee(**row_data))

    if new_employees:
        Employee.objects.bulk_create(new_employees)
    return HttpResponse("Success")


@csrf_exempt
def view_employees(request):
    return render(request, "templates/view_employees.html")


@csrf_exempt
def get_employee_data(request):
    request_data = request.GET
    json_data = copy.deepcopy(DATATABLE_RESPONSE)
    lis = ['name', 'email', 'phone_number', 'dob']
    start_index = int(request_data.get('start'))
    json_data['draw'] = int(request_data.get('draw', 0))
    stop_index = 0
    order_index = request_data.get('order[0][column]', '')
    order_term = request_data.get('order[0][dir]', '')
    order_by = 'name'
    if order_index and order_term:
        order_by = lis[int(order_index)]
        if order_term == 'desc':
            order_by = '-%s' % order_by
    search_term = request_data.get('search[value]', '')
    if search_term:
        employees = Employee.objects.filter(Q(name__icontains=search_term)|Q(email__icontains=search_term)|Q(phone_number__icontains=search_term)|
                                            Q(dob__regex=search_term)).order_by(order_by)
    else:
        employees = Employee.objects.all().order_by(order_by)
    json_data['recordsFiltered'] = employees.count()
    json_data['recordsTotal'] = json_data['recordsFiltered']
    if request_data.get('length'):
        stop_index = start_index + int(request_data.get('length'))
    for employee in employees[start_index:stop_index]:
        json_data['data'].append([employee.name, employee.email, employee.phone_number, str(employee.dob)])
    return HttpResponse(json.dumps(json_data))
