from django.shortcuts import render, redirect, get_object_or_404
from .models import Lesson, FeedbackRecord, QuizSet, Question, StudentAnswer
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json
import threading
import re
import io
import base64
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
    # 활성 퀴즈가 있는 차시 번호 집합
    active_chapters = set(
        QuizSet.objects.filter(is_active=True).values_list('chapter_num', flat=True)
    )
    lessons_by_class = OrderedDict()
    for lesson in LESSONS:
        c = lesson['class']
        if c not in lessons_by_class:
            lessons_by_class[c] = []
        entry = dict(lesson)
        entry['has_quiz'] = (lesson['id'] % 100) in active_chapters
        lessons_by_class[c].append(entry)
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


# ═══════════════════════════════════════════════════════════════
#  활동문제 채점 시스템  (Quiz System)
# ═══════════════════════════════════════════════════════════════

TEACHER_PASSWORD = os.environ.get('TEACHER_PASSWORD', 'info1234')


# ── 헬퍼: 이미지 리사이즈 → base64 ──────────────────────────────

def _resize_image_to_b64(image_bytes):
    """업로드 이미지를 최대 1200px JPEG(quality 70%)로 변환 후 base64 반환"""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        max_px = 1200
        if max(img.size) > max_px:
            ratio = max_px / max(img.size)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=70)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"이미지 처리 오류: {e}")
        return base64.b64encode(image_bytes).decode('utf-8')


# ── 헬퍼: PDF → 텍스트 ───────────────────────────────────────────

def _extract_text_from_pdf(pdf_bytes):
    """pdfplumber로 PDF 텍스트 추출"""
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
        return '\n\n'.join(parts)
    except Exception as e:
        print(f"PDF 추출 오류: {e}")
        return ''


# ── 헬퍼: Claude로 지도서 → 문제/정답 JSON 추출 ──────────────────

def _extract_questions_with_claude(guide_text, chapter_num):
    """지도서 텍스트를 Claude에게 보내 문제·정답 구조화"""
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return {'title': f'{chapter_num}차시', 'questions': []}
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""다음은 정보 교과 {chapter_num}차시 교사용 지도서 내용입니다.
학생 활동문제(연습문제·탐구·확인문제 등)와 그 모범답안을 모두 추출해 주세요.

지도서 내용:
{guide_text[:8000]}

아래 JSON 형식으로만 응답하세요 (설명 없이):
{{
  "title": "이 차시 학습 주제 제목",
  "questions": [
    {{
      "number": 1,
      "content": "학생 교과서에 나오는 문제 전문",
      "model_answer": "교사 지도서 모범답안(상세히)",
      "score": 10
    }}
  ]
}}
문제가 없으면 questions 를 빈 배열로 반환하세요."""
        msg = client.messages.create(
            model='claude-opus-4-6',
            max_tokens=4096,
            messages=[{'role': 'user', 'content': prompt}],
        )
        raw = msg.content[0].text
        m = re.search(r'\{[\s\S]*\}', raw)
        if m:
            return json.loads(m.group())
    except Exception as e:
        print(f"Claude 문제 추출 오류: {e}")
    return {'title': f'{chapter_num}차시', 'questions': []}


# ── 헬퍼: Claude로 학생 답안 채점 ────────────────────────────────

def _grade_with_claude(q_content, model_answer, ans_text, ans_code, ans_img_b64, max_score):
    """학생 답안을 Claude Haiku로 채점 → (score, feedback) 반환"""
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        return None, '자동 채점 미설정 – 교사가 직접 채점합니다.'
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""당신은 친절하고 꼼꼼한 정보 교과 교사입니다.

[문제]
{q_content}

[모범 답안]
{model_answer}

[배점] {max_score}점
"""
        if ans_text:
            prompt += f"\n[학생 텍스트 답안]\n{ans_text}\n"
        if ans_code:
            prompt += f"\n[학생 코드 답안]\n```\n{ans_code}\n```\n"
        if ans_img_b64:
            prompt += "\n[학생 사진 답안: 아래 첨부 이미지 참고]\n"

        prompt += f"""
위 답안을 채점하고 **JSON 형식으로만** 응답하세요:
{{"score": (0~{max_score} 정수), "feedback": "잘한 점과 개선할 점을 포함한 2~3문장 한국어 피드백"}}"""

        content = [{'type': 'text', 'text': prompt}]
        if ans_img_b64:
            content.append({
                'type': 'image',
                'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': ans_img_b64},
            })

        msg = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=400,
            messages=[{'role': 'user', 'content': content}],
        )
        raw = msg.content[0].text
        m = re.search(r'\{[^{}]*\}', raw)
        if m:
            r = json.loads(m.group())
            score = max(0, min(max_score, int(r.get('score', 0))))
            return score, r.get('feedback', '')
    except Exception as e:
        print(f"Claude 채점 오류: {e}")
    return None, '자동 채점 중 오류 발생 – 교사가 직접 채점합니다.'


# ── View: 교사 – 지도서 업로드 ────────────────────────────────────

def quiz_upload(request):
    """교사용: PDF 지도서 업로드 → Claude가 문제/정답 자동 추출"""
    error = success = None
    existing = QuizSet.objects.all().order_by('chapter_num')

    if request.method == 'POST':
        pw = request.POST.get('password', '')
        if pw != TEACHER_PASSWORD:
            error = '비밀번호가 올바르지 않습니다.'
        else:
            chapter_raw = request.POST.get('chapter_num', '').strip()
            pdf_file    = request.FILES.get('guide_pdf')
            manual_text = request.POST.get('manual_text', '').strip()

            if not chapter_raw:
                error = '차시 번호를 입력해주세요.'
            elif not pdf_file and not manual_text:
                error = 'PDF 파일 또는 내용 직접 입력 중 하나는 필수입니다.'
            else:
                try:
                    chapter_num = int(chapter_raw)
                    guide_text = ''
                    if pdf_file:
                        guide_text = _extract_text_from_pdf(pdf_file.read())
                    if len(guide_text) < 50 and manual_text:
                        guide_text = manual_text
                    if len(guide_text) < 50:
                        error = 'PDF에서 텍스트를 추출하지 못했습니다. 아래 직접 입력란을 사용해 주세요.'
                    else:
                        result = _extract_questions_with_claude(guide_text, chapter_num)
                        qs, _ = QuizSet.objects.update_or_create(
                            chapter_num=chapter_num,
                            defaults={
                                'title':      result.get('title', f'{chapter_num}차시 활동문제'),
                                'guide_text': guide_text,
                                'is_active':  True,
                            }
                        )
                        qs.questions.all().delete()
                        for q in result.get('questions', []):
                            Question.objects.create(
                                quizset=qs,
                                number=q.get('number', 1),
                                content=q.get('content', ''),
                                model_answer=q.get('model_answer', ''),
                                score=q.get('score', 10),
                            )
                        cnt = qs.questions.count()
                        success = f'✓ [{qs.title}] 문제 {cnt}개 등록 완료!'
                        existing = QuizSet.objects.all().order_by('chapter_num')
                except Exception as e:
                    error = f'처리 중 오류: {e}'

    return render(request, 'feedback/quiz_upload.html', {
        'error': error, 'success': success, 'existing': existing,
    })


# ── View: 학생 – 문제 풀기 ────────────────────────────────────────

def quiz_solve(request, lesson_id):
    """학생용: 학번 입력 → 문제 제시 → 답안 작성"""
    lesson = next((l for l in LESSONS if l['id'] == lesson_id), None)
    if not lesson:
        return redirect('index')

    chapter_num = lesson_id % 100
    quizset = QuizSet.objects.filter(chapter_num=chapter_num, is_active=True).first()
    if not quizset or not quizset.questions.exists():
        return render(request, 'feedback/quiz_no_quiz.html', {'lesson': lesson})

    # 이미 제출했으면 결과 페이지로
    student_id = request.GET.get('student_id', '').strip()
    if student_id:
        if StudentAnswer.objects.filter(
            question__quizset=quizset, lesson_id=lesson_id, student_id=student_id
        ).exists():
            return redirect(f'/quiz/{lesson_id}/result/?student_id={student_id}')

    return render(request, 'feedback/quiz_solve.html', {
        'lesson': lesson,
        'quizset': quizset,
        'questions': quizset.questions.all(),
        'student_id': student_id,
    })


# ── View: 학생 – 답안 제출 ────────────────────────────────────────

def quiz_submit(request, lesson_id):
    """학생 답안을 저장하고 Claude 비동기 채점 시작"""
    lesson = next((l for l in LESSONS if l['id'] == lesson_id), None)
    if not lesson or request.method != 'POST':
        return redirect('index')

    chapter_num = lesson_id % 100
    quizset = QuizSet.objects.filter(chapter_num=chapter_num, is_active=True).first()
    if not quizset:
        return redirect('index')

    student_id   = request.POST.get('student_id', '').strip()
    student_num  = request.POST.get('student_num', '').strip()
    student_name = request.POST.get('student_name', '').strip()

    if not all([student_id, student_num, student_name]):
        return redirect('quiz_solve', lesson_id=lesson_id)

    # 중복 제출 방지
    if StudentAnswer.objects.filter(
        question__quizset=quizset, lesson_id=lesson_id, student_id=student_id
    ).exists():
        return redirect(f'/quiz/{lesson_id}/result/?student_id={student_id}')

    saved = []
    for q in quizset.questions.all():
        ans_text = request.POST.get(f'ans_text_{q.id}', '').strip()
        ans_code = request.POST.get(f'ans_code_{q.id}', '').strip()
        ans_img_b64 = ''
        img_file = request.FILES.get(f'ans_img_{q.id}')
        if img_file:
            try:
                ans_img_b64 = _resize_image_to_b64(img_file.read())
            except Exception as e:
                print(f"이미지 처리 오류: {e}")

        if not any([ans_text, ans_code, ans_img_b64]):
            continue  # 빈 답안 건너뜀

        sa = StudentAnswer.objects.create(
            question=q,
            lesson_id=lesson_id,
            student_id=student_id,
            student_num=student_num,
            student_name=student_name,
            answer_text=ans_text,
            answer_code=ans_code,
            answer_image=ans_img_b64,
            max_score=q.score,
        )
        saved.append(sa)

        # ── 비동기 Claude 채점 ──
        def do_grade(sa=sa, q=q):
            score, fb = _grade_with_claude(
                q.content, q.model_answer,
                sa.answer_text, sa.answer_code, sa.answer_image,
                q.score,
            )
            sa.score = score
            sa.ai_feedback = fb
            sa.save()
        threading.Thread(target=do_grade, daemon=True).start()

    return render(request, 'feedback/quiz_submitted.html', {
        'lesson': lesson,
        'quizset': quizset,
        'student_name': student_name,
        'student_id': student_id,
        'answer_count': len(saved),
    })


# ── View: 학생 – 채점 결과 조회 ───────────────────────────────────

def quiz_result(request, lesson_id):
    """학번으로 채점 결과 조회"""
    lesson = next((l for l in LESSONS if l['id'] == lesson_id), None)
    if not lesson:
        return redirect('index')

    student_id = request.GET.get('student_id', '').strip()
    if not student_id:
        # 학번 입력 폼 표시
        return render(request, 'feedback/quiz_result.html', {
            'lesson': lesson, 'need_id': True,
        })

    chapter_num = lesson_id % 100
    quizset = QuizSet.objects.filter(chapter_num=chapter_num).first()
    answers = []
    if quizset:
        answers = list(
            StudentAnswer.objects.filter(
                question__quizset=quizset,
                lesson_id=lesson_id,
                student_id=student_id,
            ).select_related('question').order_by('question__number')
        )

    if not answers:
        return render(request, 'feedback/quiz_result.html', {
            'lesson': lesson, 'not_found': True, 'student_id': student_id,
        })

    graded     = [a for a in answers if a.score is not None]
    total      = sum(a.score for a in graded)
    max_total  = sum(a.question.score for a in answers)
    all_graded = len(graded) == len(answers)

    return render(request, 'feedback/quiz_result.html', {
        'lesson': lesson,
        'quizset': quizset,
        'answers': answers,
        'student_name': answers[0].student_name,
        'student_id': student_id,
        'total': total,
        'max_total': max_total,
        'all_graded': all_graded,
        'need_id': False,
        'not_found': False,
    })


# ── View: 교사 대시보드 ───────────────────────────────────────────

def teacher_dashboard(request):
    """교사 로그인 + 퀴즈 관리 목록"""
    if request.method == 'POST':
        pw = request.POST.get('password', '')
        if pw == TEACHER_PASSWORD:
            request.session['teacher_auth'] = True
        else:
            return render(request, 'feedback/teacher_dashboard.html',
                          {'error': '비밀번호가 올바르지 않습니다.'})

    if not request.session.get('teacher_auth'):
        return render(request, 'feedback/teacher_dashboard.html', {})

    quizsets = QuizSet.objects.prefetch_related('questions').order_by('chapter_num')
    stats = []
    for qs in quizsets:
        sub = StudentAnswer.objects.filter(question__quizset=qs)
        unconfirmed = sub.filter(is_confirmed=False, score__isnull=False).count()
        pending_grade = sub.filter(score__isnull=True).count()
        total_students = sub.values('student_id', 'lesson_id').distinct().count()
        stats.append({
            'qs': qs,
            'total_students': total_students,
            'unconfirmed': unconfirmed,
            'pending_grade': pending_grade,
        })

    return render(request, 'feedback/teacher_dashboard.html', {
        'authenticated': True,
        'stats': stats,
    })


# ── View: 교사 – QuizSet 제출 현황 ───────────────────────────────

def teacher_quiz_detail(request, quizset_id):
    if not request.session.get('teacher_auth'):
        return redirect('teacher_dashboard')

    quizset   = get_object_or_404(QuizSet, id=quizset_id)
    questions = list(quizset.questions.all())
    answers   = (StudentAnswer.objects
                 .filter(question__quizset=quizset)
                 .select_related('question')
                 .order_by('lesson_id', 'student_num'))

    # 학생별 집계
    lesson_map = {l['id']: l['title'] for l in LESSONS}
    students_by_lesson = {}
    for ans in answers:
        key = (ans.lesson_id, ans.student_id)
        lid = ans.lesson_id
        if lid not in students_by_lesson:
            students_by_lesson[lid] = {}
        if ans.student_id not in students_by_lesson[lid]:
            students_by_lesson[lid][ans.student_id] = {
                'student_num':  ans.student_num,
                'student_name': ans.student_name,
                'student_id':   ans.student_id,
                'answers':      {},
                'total': 0, 'max': 0,
                'all_confirmed': True,
            }
        d = students_by_lesson[lid][ans.student_id]
        d['answers'][ans.question.number] = ans
        if ans.score is not None:
            d['total'] += ans.score
        d['max'] += ans.question.score
        if not ans.is_confirmed:
            d['all_confirmed'] = False

    lessons_data = {
        lid: {
            'title': lesson_map.get(lid, str(lid)),
            'students': sorted(smap.values(), key=lambda x: x['student_num']),
        }
        for lid, smap in sorted(students_by_lesson.items())
    }

    return render(request, 'feedback/teacher_quiz_detail.html', {
        'quizset':      quizset,
        'questions':    questions,
        'lessons_data': lessons_data,
    })


# ── View: 교사 – 개별 학생 채점 ──────────────────────────────────

def teacher_grade_student(request, quizset_id, lesson_id, student_id):
    if not request.session.get('teacher_auth'):
        return redirect('teacher_dashboard')

    quizset = get_object_or_404(QuizSet, id=quizset_id)
    answers = list(
        StudentAnswer.objects.filter(
            question__quizset=quizset,
            lesson_id=lesson_id,
            student_id=student_id,
        ).select_related('question').order_by('question__number')
    )
    if not answers:
        return redirect('teacher_quiz_detail', quizset_id=quizset_id)

    lesson = next((l for l in LESSONS if l['id'] == int(lesson_id)), None)

    if request.method == 'POST':
        for ans in answers:
            raw_score = request.POST.get(f'score_{ans.id}', '')
            raw_fb    = request.POST.get(f'feedback_{ans.id}', '').strip()
            if raw_score != '':
                try:
                    ans.score = max(0, min(ans.question.score, int(raw_score)))
                except ValueError:
                    pass
            ans.teacher_feedback = raw_fb
            ans.is_confirmed = True
            ans.save()
        return redirect('teacher_quiz_detail', quizset_id=quizset_id)

    return render(request, 'feedback/teacher_grade_student.html', {
        'quizset':      quizset,
        'answers':      answers,
        'lesson':       lesson,
        'student_id':   student_id,
        'student_name': answers[0].student_name,
    })