import base64
import socket
import struct
import _thread
import io
import time

import requests
import face_recognition
import cv2
import numpy as np
from Human import Human

SERVER_ADDRESS = ('localhost', 8080)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # tcp
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(SERVER_ADDRESS)
server_socket.listen(5)
BUFFER_SIZE = 1024 * 60
apiKey = "HelloWorld"

BASE_IMAGE_PATH = "images/"
SOCKET_TIME_OUT = 10
# HEADER_SIZE = struct.calcsize('10si10s')
# print(str(HEADER_SIZE).center(100, '-'))
payload_size = struct.calcsize(">L")

response = requests.get("http://localhost:8089/employer")  # local server to load data from the server

if response.status_code != 200:
    raise Exception('Problem')

human_list: list[Human] = []

print(response.json())
for human in response.json():
    human['face_coding_employer'] = np.array(human['face_coding_employer'], dtype=np.float64)
    human_list.append(Human(**human))

face_codding_list = list(map(lambda human_: human_.face_coding_employer, human_list))

print(face_codding_list)


# load info from database


# def broadcast(frame):
#     ret, image = cam.read()
#     isRe, _ = cv2.imencode(".jpg", image)
#     if isRe:
#         print(len(_))
#         packed = struct.pack('<L', len(_))
#         file_.write(len(_).to_bytes(4, byteorder='big'))
#         file_.write(_)
#         file_.flush()
#         time.sleep(0.1)


def load(img: bytes):
    """
        FROM BYTES TO FRAME
    """
    data__ = np.frombuffer(img, dtype=np.int8)
    frame = cv2.imdecode(data__, cv2.IMREAD_COLOR)
    frame_ = cv2.rotate(frame, cv2.ROTATE_180)
    return frame_


clients = []


# def requestHandler(conn, address):
#     data = b''
#
#     while len(data) < payload_size:
#         data += conn.recv(4096)
#         if not data:
#             cv2.destroyAllWindows()
#             conn, addr = server_socket.accept()
#             continue
#             # receive image row data form client socket
#         packed_msg_size = data[:payload_size]
#         data = data[payload_size:]
#         msg_size = struct.unpack(">L", packed_msg_size)[0]
#         while len(data) < msg_size:
#             data += conn.recv(4096)
#         frame_data = data[:msg_size]
#         data = data[msg_size:]


def process_frame(frame):
    pass


def sendFrame(frame, size):
    # broadcast the stream to clients
    for i in clients:
        try:
            isRe, _ = cv2.imencode(".jpg", frame)
            i.write(len(_).to_bytes(4, byteorder='big'))
            i.write(_)
        except BrokenPipeError as e:
            print("Client Disconnected")
            clients.remove(i)


def streamerHandler(streamer_socket: socket.socket, streamer_address):
    new_time = time.time()
    last_time_enter = new_time
    try:
        file_from_socket = streamer_socket.makefile("rb")

        while True:
            new_time = time.time()
            packed_size = file_from_socket.read(payload_size)
            if not packed_size:
                break  # Connection closed

            size = struct.unpack('<L', packed_size)[0]
            if size == 0:
                print('empty string received')
                continue
            buffer = io.BytesIO()
            buffer.write(file_from_socket.read(size))
            frame_data = buffer.getvalue()
            frame = load(frame_data)
            if frame is None:
                break
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

            current_image_2_encode = face_recognition.face_encodings(small_frame)
            current_location = face_recognition.face_locations(small_frame)

            for (top, right, bottom, left), encoded_face in zip(current_location,
                                                                current_image_2_encode):

                matches = face_recognition.face_distance(face_encodings=face_codding_list,
                                                         face_to_compare=encoded_face)
                min_match = min(matches)
                left *= 2
                right *= 2
                bottom *= 2
                top *= 2
                if min_match < 0.5:  # conventions
                    print('There is one')
                    # time_in = time.$ pip install aiohttp[speedups]time()
                    best_index = np.argmin(matches)

                    # Draw a label with a name below the face
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    cv2.putText(frame, human_list[best_index].name_employer, (left + 6, bottom - 6), font,
                                1.0, (255, 255, 255), 1)

                    if new_time - last_time_enter > 10 and human_list[best_index].is_active:
                        last_time_enter = time.time()
                        header = {
                            "x-token": base64.b64encode("HelloWorld".encode())
                        }
                        response_ = requests.post(headers=header,
                                                  url=f"http://localhost:8089/history/{human_list[best_index].id_employer}")
                        streamer_socket.send(b'There is One')
                        if response_.status_code == 200:
                            print('history add')

                else:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, "unknown", (left + 6, bottom - 6), font,
                                1.0, (255, 255, 255), 1)

            sendFrame(frame, size)
            cv2.imshow("Received Frame", frame)

            buffer.flush()
            file_from_socket.flush()
            if cv2.waitKey(25) == ord('q'):
                break

    except Exception as e:

        print(e)


def main():
    print('listing...')
    while True:
        try:
            socket__, address = server_socket.accept()
            receivedBytes = socket__.recv(2)
            print(f'There is client at address ${address}')

            if receivedBytes == b'CL':
                clients.append(socket__.makefile('wb'))
            elif receivedBytes == b'NC':
                _thread.start_new_thread(streamerHandler, (socket__, address))
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)
            server_socket.close()


if __name__ == '__main__':
    main()
