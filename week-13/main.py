import sys, os
import sqlite3
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem

DB_PATH = os.path.join(os.path.dirname(__file__), 'student.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS profile(
                    id_student  BLOB PRIMARY KEY NOT NULL,
                    first_name  BLOB,
                    last_name   BLOB,
                    major       BLOB)""")
        conn.commit()
    finally:
        conn.close()

class StudentForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('student_form.ui', self)

        init_db()

        self.pushButton.clicked.connect(self.saveData)
        #Load Data
        self.loadData()

        self.tableWidget.cellClicked.connect(self.on_row_clicked)

        self.btn_edit.clicked.connect(self.update_record)

        self.btn_delete.clicked.connect(self.delete_record)

    def on_row_clicked(self, row, column):
        id_val = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ""
        fname  = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else ""
        lname  = self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else ""
        major  = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else ""

        self.lineEdit.setText(id_val)
        self.lineEdit_2.setText(fname)
        self.lineEdit_3.setText(lname)
        self.lineEdit_4.setText(major)


    def saveData(self):
        student_ID = self.lineEdit.text()
        first_name = self.lineEdit_2.text()
        last_name = self.lineEdit_3.text()
        major = self.lineEdit_4.text()

        #### INSERT TO DATYABASE ####
        if not all ([student_ID, first_name, last_name, major]):
            QMessageBox.warning(self, "ข้อมูลไม่ครบถ้วน", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
            return
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO profile (id_student, first_name, last_name, major) VALUES (?, ?, ?, ?)",
                (student_ID, first_name, last_name, major)
            )
            conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "บันทึกข้อมูล ล้มเหลว" , f"เกิดข้อผิดพลาด\n{e}")
            return
        finally:
            conn.close()

        QMessageBox.information(self, "สำเร็จ", "บันทึกข้อมูลสำเร็จ")



        #############################

        QMessageBox.information(
            self,
            "ข้อมูลนักศึกษา",
            f"รหัสนักศึกษา: {student_ID}\n"
            f"ชื่อ: {first_name}\n"
            f"นามสกุล: {last_name}\n"
            f"สาขา: {major}"
        )


    def loadData(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT * FROM profile")
            rows = cur.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "โหลดข้อมูลล้มเหลว", f"เกิดความผิดพลาด\n{e}")
            return
        finally:
            conn.close()

        #กำหนดแถว
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['รหัสนักศึกษา', 'ชื่อ', 'นามสกุล', 'สาขา'])

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
            cur.execute("DELETE FROM profile WHERE id_student = ?", (code,)) ##SQL
            conn.commit()
            QMessageBox.information(self, "สำเร็จ", "ลบข้อมูลเรียบร้อย")
        except Exception as e:
            QMessageBox.critical(self, "ลบข้อมูลล้มเหลว", f"เกิดความผิดพลาด\n{e}")
        finally:
            conn.close()
            self.loadData()

    def update_record(self):
        id_student = self.lineEdit.text().strip()
        first_name = self.lineEdit_2.text().strip()
        last_name = self.lineEdit_3.text().strip()
        major = self.lineEdit_4.text().strip()

        if not id_student:
            QMessageBox.warning(self, "ไม่พบรหัส", "กรุณาเลือกรายการจากตารางก่อน")
            return

        if not (first_name and last_name and major):
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลใหม่")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                UPDATE profile
                SET first_name=?, last_name=?, major=?
                WHERE id_student=?
            """, (first_name, last_name, major, id_student))
            conn.commit()
            QMessageBox.information(self, "สำเร็จ", "แก้ไขข้อมูลเรียบร้อย")
        except Exception as e:
            QMessageBox.critical(self, "แก้ไขข้อมูลล้มเหลว", f"เกิดข้อผิดพลาด\n{e}")
        finally:
            conn.close()
            self.loadData()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = StudentForm()
    window.show()
    sys.exit(app.exec_())