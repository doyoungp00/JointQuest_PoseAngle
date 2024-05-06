import cv2
import mediapipe as mp
import json
import numpy
import socket
import threading
import base64
import time

class SeverSocket:

    def __init__(self, ip, port):
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.socketOpen()
        self.connection_thread = threading.Thread(target=self.sendMessage)
        self.receiveThread = threading.Thread(target=self.receiveImages)
        self.connection_thread.start()
        self.receiveThread.start()

    def socketClose(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is close')

    def socketOpen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        self.sock.listen(1)
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is waiting for connection')
        self.conn, self.addr = self.sock.accept()
        print(u'Server socket [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ] is connected with client')

    def sendMessage(self):
        
        while True:
            try:
                message = input("요청쓰레드: ")
                self.conn.sendall(message.encode())

            except Exception as e:
                print("전송 오류: ",e)
                break


    def receiveImages(self):

        try:
            while True:
                length = self.recvall(self.conn, 64)
                if length == None:
                    cv2.destroyAllWindows()
                length1 = length.decode('utf-8')
                json_data = json.loads(self.recvall(self.conn, int(length1)).decode('utf-8'))
                encoded_image = json_data["image"]
                angle = json_data["angle"]
                if angle:
                    print(angle)
                image = numpy.frombuffer(base64.b64decode(encoded_image), numpy.uint8)
                decimg = cv2.imdecode(image, 1)
                cv2.imshow("image", decimg)
                cv2.waitKey(1)
        except Exception as e:
            print(e)
            self.socketClose()
            cv2.destroyAllWindows()
            self.socketOpen()
            self.receiveThread = threading.Thread(target=self.receiveImages)
            self.receiveThread.start()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

def main():
    server = SeverSocket('localhost', 8080)

if __name__ == "__main__":
    main()