import requests
from bs4 import BeautifulSoup

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google_trans_new import google_translator
#pip install google_trans_new

from datetime import datetime


def getTodayEnglishWordList():
    todayLearnList = []
    req = requests.get(
        "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=%EC%98%A4%EB%8A%98%EC%9D%98+%EC%98%81%EB%8B%A8%EC%96%B4&oquery=%EC%98%A4%EB%8A%98%EC%9D%98+%EC%98%81%EC%96%B4&tqi=UJaAnlprvxsssOOjbg4ssssssAh-482974")
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    wordList = soup.find('ul', 'word_lst')
    for li in wordList.find_all("li"):
        word = li.find("a", "word")
        mean = li.find("span", "mean")
        print("{0} : {1}".format(word.get_text(), mean.get_text()))
        todayLearnList.append((word.get_text(), mean.get_text()))
    return todayLearnList


class EnglishStudy:
    def __init__(self, word, mean):
        self.word = word
        self.mean = mean
        self.sentence = self.getExampleSentence(self.word)
        self.sentence_mean = self.translateEnglishToKorean(self.sentence)

    def translateEnglishToKorean(self, sentence):
        translator = google_translator()
        result = translator.translate(sentence, lang_src="en", lang_tgt="ko")
        return result

    def getExampleSentence(self, word):
        req = requests.get("https://sentence.yourdictionary.com/{0}".format(word))
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        try:
            sentenceList = soup.find('ul', 'sentence-list')
            bestData = sentenceList.find_all("li")[0]
            sentence = bestData.find("div", "sentence component").getText()
            return sentence
        except:
            secondTry = self.getExampleSentence2(word)
            return secondTry

    def getExampleSentence2(self, word):
        req = requests.get("https://www.wordhippo.com/what-is/sentences-with-the-word/{0}.html".format(word))
        html = req.text
        try:
            soup = BeautifulSoup(html, 'html.parser')
            sentenceList = soup.find('table', {"id": 'mainsentencestable'})
            bestData = sentenceList.find_all("tr")[0]
            sentence = bestData.find_all("td")[0].getText()
            return sentence
        except:
            return "null"

    def getHtmlContent(self):
        html = "<span><strong>{0} : {1}</strong></span><br></br>" \
               "<span>{2}</span><br></br><span>{3}</span><br></br>".format(self.word, self.mean, self.sentence, self.sentence_mean)
        return html

    def __str__(self):
        return ("{0}  : {1}\n{2}\n{3}\n".format(self.word, self.mean, self.sentence, self.sentence_mean))

def makeEmailContents(wordList):
    msgContents = ""
    for index, word in enumerate(wordList):
        content = EnglishStudy(word[0], word[1])
        msgContents += "<div><span>{0}. </span> {1} </div>".format(str(index+1), content.getHtmlContent())
        print(content)
    return msgContents

def setSMTPWithGmail(email, password) :
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(email, password)
    return smtp

def makeEmail(title, content) :
    msg = MIMEMultipart()
    msg['Subject'] = title
    part = MIMEText(content, "html")
    msg.attach(part)
    return msg

def sendMail(smtp, email, to, msg) :
    msg["To"] = to
    smtp.sendmail(email, to, msg.as_string())

def getToday():
    return datetime.today().strftime("%m-%d")

if __name__ == "__main__":
    email = "your@email.com"
    password = "yourPassword"
    to = "your@want.send.email"
    wordList = getTodayEnglishWordList()
    studyContent = []

    SMTP_SERVER = setSMTPWithGmail(email, password)
    msgContents = makeEmailContents(wordList)
    today = getToday()
    emailContent = makeEmail("{0} 3M 영어 공부".format(today), msgContents)
    sendMail(SMTP_SERVER, email, to, emailContent)
