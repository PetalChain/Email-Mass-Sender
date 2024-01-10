from openai import OpenAI
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QLineEdit, QFileDialog, QVBoxLayout, QHBoxLayout,  QGroupBox, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QDateTime
import sys
import mail_support
from time import sleep
import random
import datetime

def generate_content(item):
  client = OpenAI()
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=item,
    frequency_penalty=1.5,
    temperature = 1.2
  )
  return completion.choices[0].message.content

class WorkerThread(QThread):
    update_progress = pyqtSignal(str, str)
    finished = pyqtSignal(int, int)
    timeline = pyqtSignal()
    
    repeat_count = 2

    def __init__(self, greeting, content, last, name,  receivers, senders, fromreceiver):
        super().__init__()
        self.text = content
        self.receivers = receivers
        self.senders = senders
        self.greeting = greeting
        self.last = last
        self.name = name
        self.sender_count = (len(self.senders)) / 2
        self.running = True
        self.fromreceiver = fromreceiver
    def run(self):
        while int(datetime.datetime.now().strftime("%H")) > 22 or int(datetime.datetime.now().strftime("%H")) < 10:     
            self.timeline.emit()
            sleep_count = 0
            while sleep_count < 30:
                sleep(1)
                sleep_count = sleep_count + 1
                if self.running == False:
                    sleep_count = 1000
                    break
            if sleep_count == 1000:
                status = 2
                break

            pass
        status = 0

        item_content = [
                {"role": "system", "content": "You are a assistant that helps users to refactor the original text."},
                {"role": "user", "content": self.text}
            ]
        item_title = [
                {"role": "system", "content": "You are a assistant that helps users to title."},
                {"role": "user", "content": self.text}
            ]
        sender_counter = 0
        self.index = self.fromreceiver
        self.title = ''
        self.content = ''
        while self.running == True:
            if self.index == len(self.receivers):
                break
            reciver = self.receivers[self.index]
            
            try:
                if self.index % self.repeat_count == 0:
                    self.content = generate_content(item_content)
                sleep_count = 0
                while sleep_count < 75:
                    sleep(1)
                    sleep_count = sleep_count + 1
                    if self.running == False:
                        sleep_count = 1000
                        break
                if sleep_count == 1000:
                    status = 2
                    break
                if self.index % self.repeat_count == 0:
                    self.title = generate_content(item_title)
                    while "\n" in self.title:
                        sleep_count = 0
                        while sleep_count < 75:
                            sleep(1)
                            sleep_count = sleep_count + 1
                            if self.running == False:
                                sleep_count = 1000
                                break
                        if sleep_count == 1000:
                            status = 2
                            break
                        self.title = generate_content(item_title)
                if status == 2:
                    break
                email_message = mail_support.create_message(self.title, self.senders[sender_counter * 2], reciver, self.greeting+'\n\n'+self.content+'\n\n'+self.last+'\n'+self.name)
                mail_support.send_email(self.senders[sender_counter * 2], self.senders[sender_counter * 2 + 1], email_message)
                self.update_progress.emit(self.senders[sender_counter * 2], reciver)
                
                sender_counter = (int)((sender_counter + 1) % self.sender_count)
                self.index = self.index + 1
                sleep_time = 75 + random.randint(0, 150)
                sleep_count = 0
                while sleep_count < sleep_time:
                    sleep(1)
                    sleep_count = sleep_count + 1
                    if self.running == False:
                        sleep_count = 1000
                        break
                if sleep_count == 1000:
                    status = 2
                    break
            except Exception as e:
                status=1
                print("An error occurred:", str(e))
                break
        self.finished.emit(status, self.index)

    def stop(self):
        self.running = False
class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.setWindowTitle('AutoEmailSender')
        self.resize(800, 600)

        mainLayout = QVBoxLayout()

        #mail addresses for sender and receiver
        mail_address_group_box = QGroupBox('Email Addresses')
        mailLayout = QVBoxLayout()
        mailLayout.addLayout(self.create_sender_GUI())
        mailLayout.addLayout(self.create_receiver_GUI())
        mail_address_group_box.setLayout(mailLayout)
        
        mainLayout.addWidget(mail_address_group_box)

        #mailcontent
        content_group_box = QGroupBox('Email Content')
        contentLayout = QVBoxLayout()
        contentLayout.addLayout(self.create_mail_content_GUI())
        content_group_box.setLayout(contentLayout)

        mainLayout.addWidget(content_group_box)

        #logs
        log_group_box = QGroupBox('Logs')
        logLayout = QVBoxLayout()
        logLayout.addLayout(self.create_log_GUI())
        log_group_box.setLayout(logLayout)

        mainLayout.addWidget(log_group_box)

        mainLayout.addLayout(self.create_sendButton_GUI())
        self.setLayout(mainLayout)
        self.fromreceiver = 0
    
    def create_sender_GUI(self):
        senderLayout = QHBoxLayout()
        self.sender_line_edit = QLineEdit()
        self.sender_line_edit.setEnabled(False)
        senderLayout.addWidget(self.sender_line_edit)

        self.sender_open_btn = QPushButton('Email For Sender')
        self.sender_open_btn.setFixedWidth(100)
        self.sender_open_btn.clicked.connect(lambda:self.open_file_dialog(0))
        senderLayout.addWidget(self.sender_open_btn)

        return senderLayout
    def create_receiver_GUI(self):
        receiverLayout = QHBoxLayout()
        self.receiver_line_edit = QLineEdit()
        self.receiver_line_edit.setEnabled(False)
        receiverLayout.addWidget(self.receiver_line_edit)

        self.receiver_open_btn = QPushButton('Email For Receiver')
        self.receiver_open_btn.setFixedWidth(100)
        self.receiver_open_btn.clicked.connect(lambda:self.open_file_dialog(1))
        receiverLayout.addWidget(self.receiver_open_btn)

        return receiverLayout
    def create_mail_content_GUI(self):
        layout = QVBoxLayout()
        self.greeting = QLineEdit()
        self.greeting.setText('Hi')
        self.content = QTextEdit()
        self.content.setPlainText('I am a senior full-stack developer with extensive experience in web and mobile development.\nAfter the completion of my previous contract, I am actively seeking new opportunities and would be thrilled to work with you on any projects or initiatives.\n\nI am available for an interview at your convenience and eager to discuss how my skills and expertise can contribute to your business.\n\nThank you for considering my application. I look forward to the possibility of working together.\nMy hourly rate is 25$.')
        self.last = QLineEdit()
        self.last.setText('Best Regards.')
        self.name = QLineEdit()
        self.name.setText('Eric')
        self.content.setFixedHeight(350)
        layout.addWidget(self.greeting)
        layout.addWidget(self.content)
        layout.addWidget(self.last)
        layout.addWidget(self.name)
        return layout
    def create_log_GUI(self):
        layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        return layout
    def create_sendButton_GUI(self):
        layout = QHBoxLayout()
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_btn_clicked)
        layout.addWidget(self.send_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_btn_clicked)
        layout.addWidget(self.stop_button)
        return layout
    
    def open_file_dialog(self, mode):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select File')
        if file_path:
            if mode == 0:
              self.sender_line_edit.setText(file_path)
              self.senders = mail_support.parse_sender_addresses(file_path)
            else:
                self.receiver_line_edit.setText(file_path)
                self.receivers = mail_support.parse_receiver_addresses(file_path)

    def send_btn_clicked(self):
        self.send_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.content.setEnabled(False)
        self.greeting.setEnabled(False)
        self.last.setEnabled(False)
        self.name.setEnabled(False)
        self.worker_thread = WorkerThread(self.greeting.text(), self.content.toPlainText(), self.last.text(), self.name.text(), self.receivers, self.senders, self.fromreceiver)  # Pass parameter to the worker thread
        self.worker_thread.update_progress.connect(self.update_progress_label)
        self.worker_thread.finished.connect(self.worker_thread_finished)
        self.worker_thread.timeline.connect(self.timelined)
        self.worker_thread.start()

    def stop_btn_clicked(self):
        if self.worker_thread is not None and self.worker_thread.isRunning():
            self.worker_thread.stop()

    def update_progress_label(self, sender, receiver):
        # Get the current date and time
        current_datetime = QDateTime.currentDateTime()

        # Convert the datetime to a string representation
        datetime_string = current_datetime.toString(Qt.DefaultLocaleLongDate)

        self.log.setPlainText(self.log.toPlainText()+datetime_string+': FROM '+sender+' TO '+receiver+'\n')
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def worker_thread_finished(self, result, index):
        self.fromreceiver = index
        self.worker_thread = None
        self.send_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.content.setEnabled(True)
        self.greeting.setEnabled(True)
        self.last.setEnabled(True)
        self.name.setEnabled(True)
        if result == 0:
            self.log.setPlainText(self.log.toPlainText()+'Sucessfully Finished\n')
        elif result == 1:
            self.log.setPlainText(self.log.toPlainText()+'Unexpectedly Finished\n')
        elif result == 2:
            self.log.setPlainText(self.log.toPlainText()+'Paused\n')

    def timelined(self):
        self.log.setPlainText(self.log.toPlainText()+'Paused because time does not meet condition\n')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec())