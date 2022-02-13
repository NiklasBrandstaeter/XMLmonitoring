import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import concurrent.futures
import multiprocessing
from WorkerUDP import WorkerUDP
from MyMainWindow import MyMainWindow

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

mt = concurrent.futures.ThreadPoolExecutor(max_workers=10)

def createReciever(conn):
    worker = WorkerUDP(conn)
    worker.run()

def closeEvent(process):
    process.kill()

if __name__ == '__main__':
    conn_parent, conn_child = multiprocessing.Pipe()
    process = multiprocessing.Process(target=createReciever, args=(conn_child,))
    process.start()
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(lambda: closeEvent(process))
    main_window = MyMainWindow(conn_parent, conn_child)
    main_window.show()

    sys.exit(app.exec_())

