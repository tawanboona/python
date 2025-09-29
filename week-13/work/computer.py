import sys, os
import sqlite3
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem

DB_PATH = os.path.join(os.path.dirname(__file__), 'computer.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS computer (
                    "id"	BLOB PRIMARY KEY NOT NULL,
                    "id_com"	BLOB ,
                    "name_com"	BLOB,
                    "details"	BLOB,
                    "room"	BLOB,
                    "locate"	BLOB)""")
        conn.commit()
    finally:
        conn.close()

class computerForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('plasscom_form.ui', self)

        init_db()

        self.btn_save.clicked.connect(self.saveData)
        #Load Data
        self.loadData()

        self.tableWidget.cellClicked.connect(self.on_row_clicked)

        self.btn_edit.clicked.connect(self.update_record)

        self.btn_delete.clicked.connect(self.delete_record)

    def on_row_clicked(self, row, column):
        id = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ""
        id_com  = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else ""
        name_com  = self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else ""
        details  = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else ""
        room  = self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else ""
        locate  = self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else ""

        self.lineEdit.setText(id)
        self.lineEdit_2.setText(id_com)
        self.lineEdit_3.setText(name_com)
        self.lineEdit_4.setText(details)
        self.lineEdit_5.setText(room)
        self.lineEdit_6.setText(locate)


    def saveData(self):
        id = self.lineEdit.text()
        id_com = self.lineEdit_2.text()
        name_com = self.lineEdit_3.text()
        details = self.lineEdit_4.text()
        room = self.lineEdit_5.text()
        locate = self.lineEdit_6.text()

        #### INSERT TO DATYABASE ####
        if not all ([id, id_com, name_com, details, room, locate]):
            QMessageBox.warning(self, "ข้อมูลไม่ครบถ้วน", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO computer (id, id_com, name_com, details, room, locate) VALUES (?, ?, ?, ?, ?, ?)",
                (id, id_com, name_com, details, room, locate)
            )

            conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "บันทึกข้อมูล ล้มเหลว" , f"เกิดข้อผิดพลาด\n{e}")
            return
        finally:
            conn.close()

        QMessageBox.information(self, "สำเร็จ", "บันทึกข้อมูลสำเร็จ")
        self.loadData()



        #############################

        QMessageBox.information(
            self,
            "ข้อมูลครุภัณฑ์สาขาวิทยาการคอมพิวเตอร์",
            f"รหัส: {id}\n"
            f"รหัสครุภัณฑ์: {id_com}\n"
            f"ชื่อครุภัณฑ์: {name_com}\n"
            f"รายละเอียด: {details}\n"
            f"ห้อง: {room}"
            f"พิกัด: {locate}\n"
        )


    def loadData(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT * FROM computer")
            rows = cur.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "โหลดข้อมูลล้มเหลว", f"เกิดความผิดพลาด\n{e}")
            return
        finally:
            conn.close()

        #กำหนดแถว
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(['รหัส', 'รหัสครุภัณฑ์', 'ชื่อครุภัณฑ์', 'รายละเอียด', 'ห้อง', 'พิกัด'])

        #load ข้อมูลมาทีละแถว
        for r,row in enumerate(rows):
            for c, val in enumerate(row):
                self.tableWidget.setItem(r, c, QtWidgets.QTableWidgetItem(str(val)))

        self.tableWidget.resizeColumnsToContents()


    def delete_record(self):
        code = self.lineEdit.text().strip()
        if not code:
            QMessageBox.warning(self, "ไม่พบรหัส", "กรุณาเลือกรายการจากตารางก่อน")
            return

        confirm = QMessageBox.question(self, "ยืนยันการลบ", f"ต้องการลบข้อมูลหรือไม่ '{code}' ใช่หรือไม่ ",
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if confirm != QMessageBox.Yes:
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("DELETE FROM computer WHERE id = ?", (code,)) ##SQL
            conn.commit()
            QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลเรียบร้อย")
        except Exception as e:
            QMessageBox.critical(self, "ลบข้อมูลล้มเหลว", f"เกิดความผิดพลาด\n{e}")
        finally:
            conn.close()
            self.loadData()

    def update_record(self):
        id = self.lineEdit.text().strip()
        id_com = self.lineEdit_2.text().strip()
        name_com = self.lineEdit_3.text().strip()
        details = self.lineEdit_4.text().strip()
        room = self.lineEdit_5.text().strip()
        locate = self.lineEdit_6.text().strip()

        if not id:
            QMessageBox.warning(self, "ไม่พบรหัส", "กรุณาเลือกรายการจากตารางก่อน")
            return

        if not (id_com and name_com and details and room and locate):
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลใหม่")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE computer
                SET id_com=?, name_com=?, details=?, room=?, locate=?
                WHERE id=?
            """, (id_com, name_com, details, room, locate, id))
            conn.commit()
            QMessageBox.information(self, "สำเร็จ", "แก้ไขข้อมูลเรียบร้อย")
        except Exception as e:
            QMessageBox.critical(self, "แก้ไขข้อมูลล้มเหลว", f"เกิดข้อผิดพลาด\n{e}")
        finally:
            conn.close()
            self.loadData()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = computerForm()
    window.show()
    sys.exit(app.exec_())