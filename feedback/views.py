from django.shortcuts import render, redirect, get_object_or_404
from .models import Lesson, FeedbackRecord
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json
import threading
from collections import OrderedDict

def get_sheet():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    else:
        creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key('1A7awsXWOu-WPiRjY6vk8rPEhBh8PpGiTp3pGAlellsM').sheet1
    return sheet

LESSONS = [
    # 8반 (수목금)
    {'id': 101, 'title': '8반 - 1차시', 'date': '2026-04-15', 'class': '8반'},
    {'id': 102, 'title': '8반 - 2차시', 'date': '2026-04-16', 'class': '8반'},
    {'id': 103, 'title': '8반 - 3차시', 'date': '2026-04-17', 'class': '8반'},
    {'id': 104, 'title': '8반 - 4차시', 'date': '2026-04-22', 'class': '8반'},
    {'id': 105, 'title': '8반 - 5차시', 'date': '2026-04-23', 'class': '8반'},
    {'id': 106, 'title': '8반 - 6차시', 'date': '2026-04-24', 'class': '8반'},
    {'id': 107, 'title': '8반 - 7차시', 'date': '2026-04-29', 'class': '8반'},
    {'id': 108, 'title': '8반 - 8차시', 'date': '2026-04-30', 'class': '8반'},
    {'id': 109, 'title': '8반 - 9차시', 'date': '2026-05-01', 'class': '8반'},
    {'id': 110, 'title': '8반 - 10차시', 'date': '2026-05-07', 'class': '8반'},
    {'id': 111, 'title': '8반 - 11차시', 'date': '2026-05-08', 'class': '8반'},
    {'id': 112, 'title': '8반 - 12차시', 'date': '2026-05-09', 'class': '8반'},
    {'id': 113, 'title': '8반 - 13차시', 'date': '2026-05-13', 'class': '8반'},
    {'id': 114, 'title': '8반 - 14차시', 'date': '2026-05-14', 'class': '8반'},
    {'id': 115, 'title': '8반 - 15차시', 'date': '2026-05-15', 'class': '8반'},
    {'id': 116, 'title': '8반 - 16차시', 'date': '2026-05-20', 'class': '8반'},
    {'id': 117, 'title': '8반 - 17차시', 'date': '2026-05-21', 'class': '8반'},
    {'id': 118, 'title': '8반 - 18차시', 'date': '2026-05-22', 'class': '8반'},
    {'id': 119, 'title': '8반 - 19차시', 'date': '2026-05-27', 'class': '8반'},
    {'id': 120, 'title': '8반 - 20차시', 'date': '2026-05-28', 'class': '8반'},
    {'id': 121, 'title': '8반 - 21차시', 'date': '2026-05-29', 'class': '8반'},
    {'id': 122, 'title': '8반 - 22차시', 'date': '2026-06-03', 'class': '8반'},
    {'id': 123, 'title': '8반 - 23차시', 'date': '2026-06-04', 'class': '8반'},
    {'id': 124, 'title': '8반 - 24차시', 'date': '2026-06-05', 'class': '8반'},
    {'id': 125, 'title': '8반 - 25차시', 'date': '2026-06-10', 'class': '8반'},
    {'id': 126, 'title': '8반 - 26차시', 'date': '2026-06-11', 'class': '8반'},
    {'id': 127, 'title': '8반 - 27차시', 'date': '2026-06-12', 'class': '8반'},
    {'id': 128, 'title': '8반 - 28차시', 'date': '2026-06-17', 'class': '8반'},
    {'id': 129, 'title': '8반 - 29차시', 'date': '2026-06-18', 'class': '8반'},
    {'id': 130, 'title': '8반 - 30차시', 'date': '2026-06-19', 'class': '8반'},
    {'id': 131, 'title': '8반 - 31차시', 'date': '2026-06-24', 'class': '8반'},
    {'id': 132, 'title': '8반 - 32차시', 'date': '2026-06-25', 'class': '8반'},
    {'id': 133, 'title': '8반 - 33차시', 'date': '2026-06-26', 'class': '8반'},
    {'id': 134, 'title': '8반 - 34차시', 'date': '2026-07-01', 'class': '8반'},
    {'id': 135, 'title': '8반 - 35차시', 'date': '2026-07-02', 'class': '8반'},
    {'id': 136, 'title': '8반 - 36차시', 'date': '2026-07-03', 'class': '8반'},
    {'id': 137, 'title': '8반 - 37차시', 'date': '2026-07-08', 'class': '8반'},
    {'id': 138, 'title': '8반 - 38차시', 'date': '2026-07-09', 'class': '8반'},
    {'id': 139, 'title': '8반 - 39차시', 'date': '2026-07-10', 'class': '8반'},
    # 9반 (수목금)
    {'id': 201, 'title': '9반 - 1차시', 'date': '2026-04-15', 'class': '9반'},
    {'id': 202, 'title': '9반 - 2차시', 'date': '2026-04-16', 'class': '9반'},
    {'id': 203, 'title': '9반 - 3차시', 'date': '2026-04-17', 'class': '9반'},
    {'id': 204, 'title': '9반 - 4차시', 'date': '2026-04-22', 'class': '9반'},
    {'id': 205, 'title': '9반 - 5차시', 'date': '2026-04-23', 'class': '9반'},
    {'id': 206, 'title': '9반 - 6차시', 'date': '2026-04-24', 'class': '9반'},
    {'id': 207, 'title': '9반 - 7차시', 'date': '2026-04-29', 'class': '9반'},
    {'id': 208, 'title': '9반 - 8차시', 'date': '2026-04-30', 'class': '9반'},
    {'id': 209, 'title': '9반 - 9차시', 'date': '2026-05-01', 'class': '9반'},
    {'id': 210, 'title': '9반 - 10차시', 'date': '2026-05-07', 'class': '9반'},
    {'id': 211, 'title': '9반 - 11차시', 'date': '2026-05-08', 'class': '9반'},
    {'id': 212, 'title': '9반 - 12차시', 'date': '2026-05-09', 'class': '9반'},
    {'id': 213, 'title': '9반 - 13차시', 'date': '2026-05-13', 'class': '9반'},
    {'id': 214, 'title': '9반 - 14차시', 'date': '2026-05-14', 'class': '9반'},
    {'id': 215, 'title': '9반 - 15차시', 'date': '2026-05-15', 'class': '9반'},
    {'id': 216, 'title': '9반 - 16차시', 'date': '2026-05-20', 'class': '9반'},
    {'id': 217, 'title': '9반 - 17차시', 'date': '2026-05-21', 'class': '9반'},
    {'id': 218, 'title': '9반 - 18차시', 'date': '2026-05-22', 'class': '9반'},
    {'id': 219, 'title': '9반 - 19차시', 'date': '2026-05-27', 'class': '9반'},
    {'id': 220, 'title': '9반 - 20차시', 'date': '2026-05-28', 'class': '9반'},
    {'id': 221, 'title': '9반 - 21차시', 'date': '2026-05-29', 'class': '9반'},
    {'id': 222, 'title': '9반 - 22차시', 'date': '2026-06-03', 'class': '9반'},
    {'id': 223, 'title': '9반 - 23차시', 'date': '2026-06-04', 'class': '9반'},
    {'id': 224, 'title': '9반 - 24차시', 'date': '2026-06-05', 'class': '9반'},
    {'id': 225, 'title': '9반 - 25차시', 'date': '2026-06-10', 'class': '9반'},
    {'id': 226, 'title': '9반 - 26차시', 'date': '2026-06-11', 'class': '9반'},
    {'id': 227, 'title': '9반 - 27차시', 'date': '2026-06-12', 'class': '9반'},
    {'id': 228, 'title': '9반 - 28차시', 'date': '2026-06-17', 'class': '9반'},
    {'id': 229, 'title': '9반 - 29차시', 'date': '2026-06-18', 'class': '9반'},
    {'id': 230, 'title': '9반 - 30차시', 'date': '2026-06-19', 'class': '9반'},
    {'id': 231, 'title': '9반 - 31차시', 'date': '2026-06-24', 'class': '9반'},
    {'id': 232, 'title': '9반 - 32차시', 'date': '2026-06-25', 'class': '9반'},
    {'id': 233, 'title': '9반 - 33차시', 'date': '2026-06-26', 'class': '9반'},
    {'id': 234, 'title': '9반 - 34차시', 'date': '2026-07-01', 'class': '9반'},
    {'id': 235, 'title': '9반 - 35차시', 'date': '2026-07-02', 'class': '9반'},
    {'id': 236, 'title': '9반 - 36차시', 'date': '2026-07-03', 'class': '9반'},
    {'id': 237, 'title': '9반 - 37차시', 'date': '2026-07-08', 'class': '9반'},
    {'id': 238, 'title': '9반 - 38차시', 'date': '2026-07-09', 'class': '9반'},
    {'id': 239, 'title': '9반 - 39차시', 'date': '2026-07-10', 'class': '9반'},
    # 10반 (월화목)
    {'id': 301, 'title': '10반 - 1차시', 'date': '2026-04-13', 'class': '10반'},
    {'id': 302, 'title': '10반 - 2차시', 'date': '2026-04-14', 'class': '10반'},
    {'id': 303, 'title': '10반 - 3차시', 'date': '2026-04-16', 'class': '10반'},
    {'id': 304, 'title': '10반 - 4차시', 'date': '2026-04-20', 'class': '10반'},
    {'id': 305, 'title': '10반 - 5차시', 'date': '2026-04-21', 'class': '10반'},
    {'id': 306, 'title': '10반 - 6차시', 'date': '2026-04-23', 'class': '10반'},
    {'id': 307, 'title': '10반 - 7차시', 'date': '2026-04-27', 'class': '10반'},
    {'id': 308, 'title': '10반 - 8차시', 'date': '2026-04-28', 'class': '10반'},
    {'id': 309, 'title': '10반 - 9차시', 'date': '2026-04-30', 'class': '10반'},
    {'id': 310, 'title': '10반 - 10차시', 'date': '2026-05-04', 'class': '10반'},
    {'id': 311, 'title': '10반 - 11차시', 'date': '2026-05-06', 'class': '10반'},
    {'id': 312, 'title': '10반 - 12차시', 'date': '2026-05-07', 'class': '10반'},
    {'id': 313, 'title': '10반 - 13차시', 'date': '2026-05-11', 'class': '10반'},
    {'id': 314, 'title': '10반 - 14차시', 'date': '2026-05-12', 'class': '10반'},
    {'id': 315, 'title': '10반 - 15차시', 'date': '2026-05-14', 'class': '10반'},
    {'id': 316, 'title': '10반 - 16차시', 'date': '2026-05-18', 'class': '10반'},
    {'id': 317, 'title': '10반 - 17차시', 'date': '2026-05-19', 'class': '10반'},
    {'id': 318, 'title': '10반 - 18차시', 'date': '2026-05-21', 'class': '10반'},
    {'id': 319, 'title': '10반 - 19차시', 'date': '2026-05-25', 'class': '10반'},
    {'id': 320, 'title': '10반 - 20차시', 'date': '2026-05-26', 'class': '10반'},
    {'id': 321, 'title': '10반 - 21차시', 'date': '2026-05-28', 'class': '10반'},
    {'id': 322, 'title': '10반 - 22차시', 'date': '2026-06-01', 'class': '10반'},
    {'id': 323, 'title': '10반 - 23차시', 'date': '2026-06-02', 'class': '10반'},
    {'id': 324, 'title': '10반 - 24차시', 'date': '2026-06-04', 'class': '10반'},
    {'id': 325, 'title': '10반 - 25차시', 'date': '2026-06-08', 'class': '10반'},
    {'id': 326, 'title': '10반 - 26차시', 'date': '2026-06-09', 'class': '10반'},
    {'id': 327, 'title': '10반 - 27차시', 'date': '2026-06-11', 'class': '10반'},
    {'id': 328, 'title': '10반 - 28차시', 'date': '2026-06-15', 'class': '10반'},
    {'id': 329, 'title': '10반 - 29차시', 'date': '2026-06-16', 'class': '10반'},
    {'id': 330, 'title': '10반 - 30차시', 'date': '2026-06-18', 'class': '10반'},
    {'id': 331, 'title': '10반 - 31차시', 'date': '2026-06-22', 'class': '10반'},
    {'id': 332, 'title': '10반 - 32차시', 'date': '2026-06-23', 'class': '10반'},
    {'id': 333, 'title': '10반 - 33차시', 'date': '2026-06-25', 'class': '10반'},
    {'id': 334, 'title': '10반 - 34차시', 'date': '2026-06-29', 'class': '10반'},
    {'id': 335, 'title': '10반 - 35차시', 'date': '2026-06-30', 'class': '10반'},
    {'id': 336, 'title': '10반 - 36차시', 'date': '2026-07-02', 'class': '10반'},
    {'id': 337, 'title': '10반 - 37차시', 'date': '2026-07-06', 'class': '10반'},
    {'id': 338, 'title': '10반 - 38차시', 'date': '2026-07-07', 'class': '10반'},
    {'id': 339, 'title': '10반 - 39차시', 'date': '2026-07-09', 'class': '10반'},
    # 11반 (월수금)
    {'id': 401, 'title': '11반 - 1차시', 'date': '2026-04-13', 'class': '11반'},
    {'id': 402, 'title': '11반 - 2차시', 'date': '2026-04-15', 'class': '11반'},
    {'id': 403, 'title': '11반 - 3차시', 'date': '2026-04-17', 'class': '11반'},
    {'id': 404, 'title': '11반 - 4차시', 'date': '2026-04-20', 'class': '11반'},
    {'id': 405, 'title': '11반 - 5차시', 'date': '2026-04-22', 'class': '11반'},
    {'id': 406, 'title': '11반 - 6차시', 'date': '2026-04-24', 'class': '11반'},
    {'id': 407, 'title': '11반 - 7차시', 'date': '2026-04-27', 'class': '11반'},
    {'id': 408, 'title': '11반 - 8차시', 'date': '2026-04-29', 'class': '11반'},
    {'id': 409, 'title': '11반 - 9차시', 'date': '2026-05-01', 'class': '11반'},
    {'id': 410, 'title': '11반 - 10차시', 'date': '2026-05-04', 'class': '11반'},
    {'id': 411, 'title': '11반 - 11차시', 'date': '2026-05-06', 'class': '11반'},
    {'id': 412, 'title': '11반 - 12차시', 'date': '2026-05-08', 'class': '11반'},
    {'id': 413, 'title': '11반 - 13차시', 'date': '2026-05-11', 'class': '11반'},
    {'id': 414, 'title': '11반 - 14차시', 'date': '2026-05-13', 'class': '11반'},
    {'id': 415, 'title': '11반 - 15차시', 'date': '2026-05-15', 'class': '11반'},
    {'id': 416, 'title': '11반 - 16차시', 'date': '2026-05-18', 'class': '11반'},
    {'id': 417, 'title': '11반 - 17차시', 'date': '2026-05-20', 'class': '11반'},
    {'id': 418, 'title': '11반 - 18차시', 'date': '2026-05-22', 'class': '11반'},
    {'id': 419, 'title': '11반 - 19차시', 'date': '2026-05-25', 'class': '11반'},
    {'id': 420, 'title': '11반 - 20차시', 'date': '2026-05-27', 'class': '11반'},
    {'id': 421, 'title': '11반 - 21차시', 'date': '2026-05-29', 'class': '11반'},
    {'id': 422, 'title': '11반 - 22차시', 'date': '2026-06-01', 'class': '11반'},
    {'id': 423, 'title': '11반 - 23차시', 'date': '2026-06-03', 'class': '11반'},
    {'id': 424, 'title': '11반 - 24차시', 'date': '2026-06-05', 'class': '11반'},
    {'id': 425, 'title': '11반 - 25차시', 'date': '2026-06-08', 'class': '11반'},
    {'id': 426, 'title': '11반 - 26차시', 'date': '2026-06-10', 'class': '11반'},
    {'id': 427, 'title': '11반 - 27차시', 'date': '2026-06-12', 'class': '11반'},
    {'id': 428, 'title': '11반 - 28차시', 'date': '2026-06-15', 'class': '11반'},
    {'id': 429, 'title': '11반 - 29차시', 'date': '2026-06-17', 'class': '11반'},
    {'id': 430, 'title': '11반 - 30차시', 'date': '2026-06-19', 'class': '11반'},
    {'id': 431, 'title': '11반 - 31차시', 'date': '2026-06-22', 'class': '11반'},
    {'id': 432, 'title': '11반 - 32차시', 'date': '2026-06-24', 'class': '11반'},
    {'id': 433, 'title': '11반 - 33차시', 'date': '2026-06-26', 'class': '11반'},
    {'id': 434, 'title': '11반 - 34차시', 'date': '2026-06-29', 'class': '11반'},
    {'id': 435, 'title': '11반 - 35차시', 'date': '2026-07-01', 'class': '11반'},
    {'id': 436, 'title': '11반 - 36차시', 'date': '2026-07-03', 'class': '11반'},
    {'id': 437, 'title': '11반 - 37차시', 'date': '2026-07-06', 'class': '11반'},
    {'id': 438, 'title': '11반 - 38차시', 'date': '2026-07-08', 'class': '11반'},
    {'id': 439, 'title': '11반 - 39차시', 'date': '2026-07-10', 'class': '11반'},
    # 12반 (월화수)
    {'id': 501, 'title': '12반 - 1차시', 'date': '2026-04-13', 'class': '12반'},
    {'id': 502, 'title': '12반 - 2차시', 'date': '2026-04-14', 'class': '12반'},
    {'id': 503, 'title': '12반 - 3차시', 'date': '2026-04-15', 'class': '12반'},
    {'id': 504, 'title': '12반 - 4차시', 'date': '2026-04-20', 'class': '12반'},
    {'id': 505, 'title': '12반 - 5차시', 'date': '2026-04-21', 'class': '12반'},
    {'id': 506, 'title': '12반 - 6차시', 'date': '2026-04-22', 'class': '12반'},
    {'id': 507, 'title': '12반 - 7차시', 'date': '2026-04-27', 'class': '12반'},
    {'id': 508, 'title': '12반 - 8차시', 'date': '2026-04-28', 'class': '12반'},
    {'id': 509, 'title': '12반 - 9차시', 'date': '2026-04-29', 'class': '12반'},
    {'id': 510, 'title': '12반 - 10차시', 'date': '2026-05-04', 'class': '12반'},
    {'id': 511, 'title': '12반 - 11차시', 'date': '2026-05-06', 'class': '12반'},
    {'id': 512, 'title': '12반 - 12차시', 'date': '2026-05-07', 'class': '12반'},
    {'id': 513, 'title': '12반 - 13차시', 'date': '2026-05-11', 'class': '12반'},
    {'id': 514, 'title': '12반 - 14차시', 'date': '2026-05-12', 'class': '12반'},
    {'id': 515, 'title': '12반 - 15차시', 'date': '2026-05-13', 'class': '12반'},
    {'id': 516, 'title': '12반 - 16차시', 'date': '2026-05-18', 'class': '12반'},
    {'id': 517, 'title': '12반 - 17차시', 'date': '2026-05-19', 'class': '12반'},
    {'id': 518, 'title': '12반 - 18차시', 'date': '2026-05-20', 'class': '12반'},
    {'id': 519, 'title': '12반 - 19차시', 'date': '2026-05-25', 'class': '12반'},
    {'id': 520, 'title': '12반 - 20차시', 'date': '2026-05-26', 'class': '12반'},
    {'id': 521, 'title': '12반 - 21차시', 'date': '2026-05-27', 'class': '12반'},
    {'id': 522, 'title': '12반 - 22차시', 'date': '2026-06-01', 'class': '12반'},
    {'id': 523, 'title': '12반 - 23차시', 'date': '2026-06-02', 'class': '12반'},
    {'id': 524, 'title': '12반 - 24차시', 'date': '2026-06-03', 'class': '12반'},
    {'id': 525, 'title': '12반 - 25차시', 'date': '2026-06-08', 'class': '12반'},
    {'id': 526, 'title': '12반 - 26차시', 'date': '2026-06-09', 'class': '12반'},
    {'id': 527, 'title': '12반 - 27차시', 'date': '2026-06-10', 'class': '12반'},
    {'id': 528, 'title': '12반 - 28차시', 'date': '2026-06-15', 'class': '12반'},
    {'id': 529, 'title': '12반 - 29차시', 'date': '2026-06-16', 'class': '12반'},
    {'id': 530, 'title': '12반 - 30차시', 'date': '2026-06-17', 'class': '12반'},
    {'id': 531, 'title': '12반 - 31차시', 'date': '2026-06-22', 'class': '12반'},
    {'id': 532, 'title': '12반 - 32차시', 'date': '2026-06-23', 'class': '12반'},
    {'id': 533, 'title': '12반 - 33차시', 'date': '2026-06-24', 'class': '12반'},
    {'id': 534, 'title': '12반 - 34차시', 'date': '2026-06-29', 'class': '12반'},
    {'id': 535, 'title': '12반 - 35차시', 'date': '2026-06-30', 'class': '12반'},
    {'id': 536, 'title': '12반 - 36차시', 'date': '2026-07-01', 'class': '12반'},
    {'id': 537, 'title': '12반 - 37차시', 'date': '2026-07-06', 'class': '12반'},
    {'id': 538, 'title': '12반 - 38차시', 'date': '2026-07-07', 'class': '12반'},
    {'id': 539, 'title': '12반 - 39차시', 'date': '2026-07-08', 'class': '12반'},
    # 13반 (월화목)
    {'id': 601, 'title': '13반 - 1차시', 'date': '2026-04-13', 'class': '13반'},
    {'id': 602, 'title': '13반 - 2차시', 'date': '2026-04-14', 'class': '13반'},
    {'id': 603, 'title': '13반 - 3차시', 'date': '2026-04-16', 'class': '13반'},
    {'id': 604, 'title': '13반 - 4차시', 'date': '2026-04-20', 'class': '13반'},
    {'id': 605, 'title': '13반 - 5차시', 'date': '2026-04-21', 'class': '13반'},
    {'id': 606, 'title': '13반 - 6차시', 'date': '2026-04-23', 'class': '13반'},
    {'id': 607, 'title': '13반 - 7차시', 'date': '2026-04-27', 'class': '13반'},
    {'id': 608, 'title': '13반 - 8차시', 'date': '2026-04-28', 'class': '13반'},
    {'id': 609, 'title': '13반 - 9차시', 'date': '2026-04-30', 'class': '13반'},
    {'id': 610, 'title': '13반 - 10차시', 'date': '2026-05-04', 'class': '13반'},
    {'id': 611, 'title': '13반 - 11차시', 'date': '2026-05-06', 'class': '13반'},
    {'id': 612, 'title': '13반 - 12차시', 'date': '2026-05-07', 'class': '13반'},
    {'id': 613, 'title': '13반 - 13차시', 'date': '2026-05-11', 'class': '13반'},
    {'id': 614, 'title': '13반 - 14차시', 'date': '2026-05-12', 'class': '13반'},
    {'id': 615, 'title': '13반 - 15차시', 'date': '2026-05-14', 'class': '13반'},
    {'id': 616, 'title': '13반 - 16차시', 'date': '2026-05-18', 'class': '13반'},
    {'id': 617, 'title': '13반 - 17차시', 'date': '2026-05-19', 'class': '13반'},
    {'id': 618, 'title': '13반 - 18차시', 'date': '2026-05-21', 'class': '13반'},
    {'id': 619, 'title': '13반 - 19차시', 'date': '2026-05-25', 'class': '13반'},
    {'id': 620, 'title': '13반 - 20차시', 'date': '2026-05-26', 'class': '13반'},
    {'id': 621, 'title': '13반 - 21차시', 'date': '2026-05-28', 'class': '13반'},
    {'id': 622, 'title': '13반 - 22차시', 'date': '2026-06-01', 'class': '13반'},
    {'id': 623, 'title': '13반 - 23차시', 'date': '2026-06-02', 'class': '13반'},
    {'id': 624, 'title': '13반 - 24차시', 'date': '2026-06-04', 'class': '13반'},
    {'id': 625, 'title': '13반 - 25차시', 'date': '2026-06-08', 'class': '13반'},
    {'id': 626, 'title': '13반 - 26차시', 'date': '2026-06-09', 'class': '13반'},
    {'id': 627, 'title': '13반 - 27차시', 'date': '2026-06-11', 'class': '13반'},
    {'id': 628, 'title': '13반 - 28차시', 'date': '2026-06-15', 'class': '13반'},
    {'id': 629, 'title': '13반 - 29차시', 'date': '2026-06-16', 'class': '13반'},
    {'id': 630, 'title': '13반 - 30차시', 'date': '2026-06-18', 'class': '13반'},
    {'id': 631, 'title': '13반 - 31차시', 'date': '2026-06-22', 'class': '13반'},
    {'id': 632, 'title': '13반 - 32차시', 'date': '2026-06-23', 'class': '13반'},
    {'id': 633, 'title': '13반 - 33차시', 'date': '2026-06-25', 'class': '13반'},
    {'id': 634, 'title': '13반 - 34차시', 'date': '2026-06-29', 'class': '13반'},
    {'id': 635, 'title': '13반 - 35차시', 'date': '2026-06-30', 'class': '13반'},
    {'id': 636, 'title': '13반 - 36차시', 'date': '2026-07-02', 'class': '13반'},
    {'id': 637, 'title': '13반 - 37차시', 'date': '2026-07-06', 'class': '13반'},
    {'id': 638, 'title': '13반 - 38차시', 'date': '2026-07-07', 'class': '13반'},
    {'id': 639, 'title': '13반 - 39차시', 'date': '2026-07-09', 'class': '13반'},
]

def index(request):
    lessons_by_class = OrderedDict()
    for lesson in LESSONS:
        c = lesson['class']
        if c not in lessons_by_class:
            lessons_by_class[c] = []
        lessons_by_class[c].append(lesson)
    return render(request, 'feedback/index.html', {'lessons_by_class': lessons_by_class})

def feedback_create(request, lesson_id):
    lesson = next((l for l in LESSONS if l['id'] == lesson_id), None)
    if not lesson:
        return redirect('index')

    if request.method == 'POST':
        student_id   = request.POST['student_id'].strip()
        student_num  = request.POST['student_num'].strip()
        student_name = request.POST['student_name'].strip()
        summary      = request.POST['summary'].strip()
        problem      = request.POST['problem'].strip()
        career       = request.POST['career'].strip()
        deeplearn    = request.POST['deeplearn'].strip()
        peer         = request.POST['peer'].strip()

        # 빈 칸 서버측 검증
        if not all([student_id, student_num, student_name,
                    summary, problem, career, deeplearn, peer]):
            return render(request, 'feedback/create.html', {
                'lesson': lesson,
                'error': '모든 항목을 입력해주세요!',
                'prev': request.POST,
                'is_edit': False,
            })

        # 최소 글자수 검증
        if any(len(x) < 2 for x in [summary, problem, career, deeplearn, peer]):
            return render(request, 'feedback/create.html', {
                'lesson': lesson,
                'error': '각 항목을 좀 더 자세히 입력해주세요! (최소 2자 이상)',
                'prev': request.POST,
                'is_edit': False,
            })

        already = False
        try:
            sheet = get_sheet()
            records = sheet.get_all_values()
            for row in records[1:]:
                if len(row) >= 5 and row[2] == str(lesson_id) and row[4] == student_id:
                    already = True
                    break
        except Exception as e:
            print(f"중복 확인 오류: {e}")

        if not already:
            def save_to_sheet():
                try:
                    sheet = get_sheet()
                    sheet.append_row([
                        datetime.now().strftime('%Y-%m-%d %H:%M'),
                        lesson['title'],
                        str(lesson_id),
                        student_num,
                        student_id,
                        student_name,
                        summary,
                        problem,
                        career,
                        deeplearn,
                        peer,
                    ])
                except Exception as e:
                    print(f"구글 시트 저장 오류: {e}")
            threading.Thread(target=save_to_sheet).start()

        return render(request, 'feedback/done.html', {
            'lesson': lesson,
            'already': already,
        })

    return render(request, 'feedback/create.html', {
        'lesson': lesson,
        'prev': {},
        'is_edit': False,
        'error': None,
    })


def feedback_edit(request, lesson_id, student_id):
    lesson = next((l for l in LESSONS if l['id'] == lesson_id), None)
    if not lesson:
        return redirect('index')

    # 기존 데이터 불러오기
    existing = {}
    row_index = None
    try:
        sheet = get_sheet()
        records = sheet.get_all_values()
        for i, row in enumerate(records[1:], start=2):
            if len(row) >= 5 and row[2] == str(lesson_id) and row[4] == student_id:
                existing = {
                    'student_id':   row[4],
                    'student_num':  row[3],
                    'student_name': row[5],
                    'summary':      row[6] if len(row) > 6 else '',
                    'problem':      row[7] if len(row) > 7 else '',
                    'career':       row[8] if len(row) > 8 else '',
                    'deeplearn':    row[9] if len(row) > 9 else '',
                    'peer':         row[10] if len(row) > 10 else '',
                }
                row_index = i
                break
    except Exception as e:
        print(f"데이터 불러오기 오류: {e}")

    if not existing:
        return redirect('index')

    if request.method == 'POST':
        summary   = request.POST['summary'].strip()
        problem   = request.POST['problem'].strip()
        career    = request.POST['career'].strip()
        deeplearn = request.POST['deeplearn'].strip()
        peer      = request.POST['peer'].strip()

        if any(len(x) < 2 for x in [summary, problem, career, deeplearn, peer]):
            return render(request, 'feedback/create.html', {
                'lesson': lesson,
                'error': '각 항목을 좀 더 자세히 입력해주세요!',
                'prev': request.POST,
                'is_edit': True,
            })

        # 구글 시트 해당 행 수정
        def update_sheet():
            try:
                sheet = get_sheet()
                sheet.update(f'G{row_index}:K{row_index}', [[
                    summary, problem, career, deeplearn, peer
                ]])
                # A열 수정시간 업데이트
                sheet.update(f'A{row_index}', [[
                    datetime.now().strftime('%Y-%m-%d %H:%M') + ' (수정)'
                ]])
            except Exception as e:
                print(f"수정 오류: {e}")
        threading.Thread(target=update_sheet).start()

        return render(request, 'feedback/done.html', {
            'lesson': lesson,
            'already': False,
            'is_edit': True,
        })

    return render(request, 'feedback/create.html', {
        'lesson': lesson,
        'prev': existing,
        'is_edit': True,
        'error': None,
    })

def lesson_result(request, lesson_id):
    lesson = next((l for l in LESSONS if l['id'] == lesson_id), None)
    if not lesson:
        return redirect('index')

    student_id = request.GET.get('student_id', '').strip()
    record = None
    error  = None

    if student_id:
        try:
            sheet = get_sheet()
            records = sheet.get_all_values()
            for row in records[1:]:
                if len(row) >= 5 and row[2] == str(lesson_id) and row[4] == student_id:
                    record = {
                        'student_id':   row[4],   # ← 이 줄 추가!
                        'student_num':  row[3],
                        'student_name': row[5],
                        'summary':      row[6] if len(row) > 6 else '',
                        'problem':      row[7] if len(row) > 7 else '',
                        'career':       row[8] if len(row) > 8 else '',
                        'deeplearn':    row[9] if len(row) > 9 else '',
                        'peer':         row[10] if len(row) > 10 else '',
                    }
                    break
            if not record:
                error = "해당 학번의 제출 기록이 없습니다."
        except Exception as e:
            error = "조회 중 오류가 발생했습니다."

    return render(request, 'feedback/result.html', {
        'lesson': lesson,
        'record': record,
        'error': error,
        'student_id': student_id,
    })

def student_summary(request, student_id):
    try:
        sheet = get_sheet()
        records = sheet.get_all_values()
        student_records = []
        student_name = ''
        for row in records[1:]:
            if len(row) >= 5 and row[4] == student_id:
                student_name = row[5] if len(row) > 5 else ''
                student_records.append({
                    'date':         row[0],
                    'lesson_title': row[1],
                    'summary':      row[6] if len(row) > 6 else '',
                    'problem':      row[7] if len(row) > 7 else '',
                    'career':       row[8] if len(row) > 8 else '',
                    'deeplearn':    row[9] if len(row) > 9 else '',
                    'peer':         row[10] if len(row) > 10 else '',
                })
    except Exception as e:
        student_records = []
        student_name = ''

    if not student_records:
        return render(request, 'feedback/not_found.html')

    return render(request, 'feedback/student_summary.html', {
        'records':      student_records,
        'student_name': student_name,
        'student_id':   student_id,
        'count':        len(student_records),
    })