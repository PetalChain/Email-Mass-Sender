from openai import OpenAI
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QLineEdit, QFileDialog, QVBoxLayout, QHBoxLayout,  QGroupBox, QTextEdit
import sys
import mail_support

def generate_content(item):
  client = OpenAI()
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=item,
    frequency_penalty=1.5,
    temperature = 1.2
  )
  return completion.choices[0].message.content

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
        self.content = QTextEdit()
        self.content.setFixedHeight(350)
        layout.addWidget(self.content)
        return layout
    def create_log_GUI(self):
        layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setEnabled(False)
        layout.addWidget(self.log)
        return layout
    def create_sendButton_GUI(self):
        layout = QHBoxLayout()
        self.send_button = QPushButton('Send')
        self.send_button.clicked.connect(self.send_mail)
        layout.addWidget(self.send_button)

        return layout
    
    def open_file_dialog(self, mode):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select File')
        if file_path:
            if mode == 0:
              self.sender_line_edit.setText(file_path)
            else:
                self.receiver_line_edit.setText(file_path)
    def send_mail(self):
        item = [
          {"role": "system", "content": "You are a assistant that helps users to refactor the original text."},
          {"role": "user", "content": self.content.toPlainText()}
        ]
        email_message = mail_support.create_message('Colloboration', 'ericgall90@gmail.com', 'royleesh77@gmail.com', generate_content(item))
        mail_support.send_email('ericgall90@gmail.com', 'ayux ppaf ozff nyyu', email_message)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec())