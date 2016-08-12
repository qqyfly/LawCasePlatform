#! /usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
import re
import os
import traceback
import sys
import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import time
import threading
import Queue
from multiprocessing import Pool
import getopt
import codecs

file_folder = '/home/pierre/dev/Data/案件类型为民事案件20160810/'
export_folder = "/home/pierre/dev/Workspaces/PycharmProjects/LawCasePlatform/export/"
result_folder = "/home/pierre/dev/Workspaces/PycharmProjects/LawCasePlatform/result/"


# valid step
# 1：批量初始化处理文件
# 2：批量分析文件
step = 2


def init(num):
    if num == 1 or num == 0:
        os.popen('rm -rf /home/pierre/dev/Workspaces/PycharmProjects/LawCasePlatform/export/*')
        #os.popen('mkdir /home/pierre/dev/Workspaces/PycharmProjects/LawCasePlatform/export/')
    if num == 2 or num == 0:
        os.popen('rm -rf /home/pierre/dev/Workspaces/PycharmProjects/LawCasePlatform/result/*')
        #os.popen('mkdir /home/pierre/dev/Workspaces/PycharmProjects/LawCasePlatform/result/')


def pre_process_law_file(file_id, file_path):
    try:
        file_object = open(file_path)
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()

        soup = BeautifulSoup(''.join(all_the_text))

        # 法院名称
        court_a = soup.find("a", {"name": "DSRXX", "type": "dir"})
        court_obj = court_a.findNext("div")
        court_obj_text = court_obj.string

        # 裁决文书类型
        doctype_a = court_a.findNext("a", {"name": "SSJL", "type": "dir"})
        doctype_obj = doctype_a.findNext("div")
        doctype_obj_text = doctype_obj.string

        # 文书号码
        docno_a = doctype_a.findNext("a", {"name": "AJJBQK", "type": "dir"})
        docno_obj = docno_a.findNext("div")
        docno_obj_text = docno_obj.string

        # 申请人
        proposer_a = docno_a.findNext("a", {"name": "CPYZ", "type": "dir"})
        proposer_obj = proposer_a.findNext("div")
        proposer_obj_text = proposer_obj.string

        # 申请人代理人
        proposer_agent_a = proposer_a.findNext("a", {"name": "PJJG", "type": "dir"})
        proposer_agent_obj = proposer_agent_a.findNext("div")
        proposer_agent_obj_text = proposer_agent_obj.string

        # 被申请人
        respondent_a = proposer_agent_a.findNext("a", {"name": "WBSB", "type": "dir"})
        respondent_obj = respondent_a.findNext("div")
        respondent_obj_text = respondent_obj.string

        # 被申请人代理人
        respondent_agent_a = respondent_a.findNext("a", {"name": "WBWB", "type": "dir"})
        respondent_agent_obj = respondent_agent_a.findNext("div")
        respondent_agent_obj_text = respondent_agent_obj.string

        # 正文
        doc_content_text = ""
        content_div_obj = respondent_agent_obj.findNext('div', style=re.compile('TEXT-ALIGN:justify;'))

        while content_div_obj:
            doc_content_text = doc_content_text + content_div_obj.string + "\n"
            content_div_obj = content_div_obj.findNext('div', style=re.compile('TEXT-ALIGN:justify;'))

        # 审判员情况
        judge_obj = soup.find('div', style=re.compile('TEXT-ALIGN: right; LINE-HEIGHT: 25pt;'))

        judge_text = ""
        while judge_obj:
            judge_text = judge_text + judge_obj.string + "\n"
            judge_obj = judge_obj.findNext('div', style=re.compile('TEXT-ALIGN: right; LINE-HEIGHT: 25pt;'))

        doctype_obj_text.replace(" ", "")
        '''
        print "================文件信息================"
        print file_path

        print "================法院信息================"
        print court_obj_text
        print "================裁决文书类型================"
        print doctype_obj_text.replace(" ", "")
        print "================文书号码================"
        print docno_obj_text
        print "================申请人================"
        print proposer_obj_text
        print "================申请代理人================"
        print proposer_agent_obj_text
        print "================被申请人================"
        print respondent_obj_text
        print "================被申请代理人================"
        print respondent_agent_obj_text
        print "================案情说明================"
        print doc_content_text
        print "================审判员情况================"
        print judge_text

        '''

        # 对输出内容进行过滤
        # start_index = doc_content_text.find("本院")
        # if start_index:
        #    export_content_txt(processed_count, doc_content_text[start_index:])

        export_content_txt(file_id, doc_content_text)

    except Exception, e:
        '''
        exception_str = traceback.format_exc()
        print "Exception 发生，当前文件" + file_path + "跳转下一文件"
        print exception_str
        '''



def export_content_txt(num, content_text):
    export_filename = '%s%d.txt' %(export_folder, num)
    file_object_w = open(export_filename, "w")
    file_object_w.write(content_text)
    file_object_w.close()


def export_result_txt(file_path,content_text,result_text):
    file_object_w = open(file_path, "w")
    file_object_w.write(result_text)
    file_object_w.write("\n=========原始文件内容=============\n")
    file_object_w.write(content_text)
    file_object_w.close()


def get_file_list(p):
    p = str(p)

    a = os.listdir(p)
    b = [x for x in a if os.path.isfile(p + x)]
    return b


def get_filepath_list(p):
    p = str(p)

    a = os.listdir(p)
    b = [p+x for x in a if os.path.isfile(p + x)]
    return b

def process_content_file(file_path):

    text = codecs.open(file_path, 'r').read()
    tr4w = TextRank4Keyword()

    tr4w.analyze(text=text, lower=True, window=2)

    result_content = ""
    result_content += "关键词：\n"

    for item in tr4w.get_keywords(20, word_min_len=1):
        result_content += item.word;
        result_content += " ";
        result_content += str(item.weight);
        result_content += "\n";

    result_content += "关键短语：\n"

    for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num=2):
        result_content += phrase;
        result_content += "\n";

    tr4s = TextRank4Sentence()
    tr4s.analyze(text=text, lower=True, source='all_filters')

    result_content += "摘要：\n"

    for item in tr4s.get_key_sentences(num=3):
        result_content += str(item.weight);
        result_content += " ";
        result_content += item.sentence;
        result_content += "\n";

    export_result_txt(result_folder+os.path.basename(file_path), text, result_content)


if __name__ == '__main__':
    # 设置编码
    #reload(sys)
    #sys.setdefaultencoding('utf-16')

    # 初始化
    init(step)

    start_time = time.time()

    if step == 1 or step == 0:
        # 取得文件列表
        file_names = get_filepath_list(file_folder)

        # 依次初始化处理文件
        pool = Pool()

        for i in xrange(len(file_names)):
            pool.apply_async(pre_process_law_file, (i, file_names[i],))

        pool.close()
        pool.join()

    if step == 2 or step == 0:
        file_names = get_filepath_list(export_folder)
        print file_names
        pool = Pool()
        for i in xrange(len(file_names)):
            pool.apply_async(process_content_file, (file_names[i],))
        pool.close()
        pool.join()

    print 'Done! Time taken: {}'.format(time.time() - start_time)