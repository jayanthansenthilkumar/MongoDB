from flask import Flask, request, jsonify, session, redirect, render_template, send_file, after_this_request
from pymongo import MongoClient
import os
import tempfile
from datetime import datetime
import traceback
import io

# Replace pdfkit/wkhtmltopdf with ReportLab
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    reportlab_available = True
except ImportError:
    print("ReportLab not installed. PDF generation will not work.")
    print("Install it with: pip install reportlab")
    reportlab_available = False

app = Flask(__name__)
app.secret_key = os.urandom(24)
client = MongoClient("mongodb://localhost:27017/")
db = client["MIC"]
faculty = db["faculty"]
students = db["student"]

@app.route("/")
def home():
    if "username" in session:
        return redirect("/dashboard")
    with open("index.html", "r") as f:
        return f.read()

@app.route("/styles.css")
def styles():
    with open("styles.css", "r") as f:
        return f.read(), 200, {"Content-Type": "text/css"}

@app.route("/script.js")
def script():
    with open("script.js", "r") as f:
        return f.read(), 200, {"Content-Type": "application/javascript"}

@app.route("/dashboard.css")
def dashboard_css():
    with open("dashboard.css", "r") as f:
        return f.read(), 200, {"Content-Type": "text/css"}

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    try:
        faculty_id = int(data["fid"])
        faculty_member = faculty.find_one({"fid": faculty_id})
        if faculty_member and faculty_member["password"] == data["password"]:
            session["username"] = faculty_member["name"]
            session["fid"] = faculty_member["fid"]
            session["dept"] = faculty_member["dept"]
            session["role"] = faculty_member["role"]
            return jsonify(
                {
                    "status": "success",
                    "message": f'Welcome back, {faculty_member["name"]}!',
                }
            )
        return (
            jsonify(
                {"status": "error", "message": "Invalid credentials. Please try again."}
            ),
            401,
        )
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid Faculty ID format"}), 400

@app.route("/student-login", methods=["POST"])
def student_login():
    data = request.json
    if not data or "sid" not in data or "pass" not in data:
        return jsonify({"status": "error", "message": "Missing credentials"}), 400
    try:
        sid = str(data["sid"]).strip()
        password = str(data["pass"])
        student = students.find_one({"sid": sid})
        if student and student.get("pass") == password:
            session["user_type"] = "student"
            session["username"] = student.get("sname", "Student")
            session["sid"] = sid
            session["dept"] = student.get("dept", "")
            session["year"] = student.get("year", "")
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f'Welcome back, {student.get("sname", "Student")}!',
                        "redirect": "/student-dashboard",
                    }
                ),
                200,
            )
        return (
            jsonify(
                {"status": "error", "message": "Invalid credentials. Please try again."}
            ),
            401,
        )
    except Exception as e:
        return (
            jsonify({"status": "error", "message": "An error occurred during login"}),
            500,
        )

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/")
    dept_students_count = students.count_documents({"dept": session["dept"]})
    total_students = students.count_documents({})
    attendance_percent = 85
    pending_tasks = 3
    with open("dashboard.html", "r") as f:
        html = f.read()
        html = html.replace("{username}", session["username"])
        html = html.replace("{department}", session["dept"])
        html = html.replace("{role}", session.get("role", ""))
        html = html.replace("{fid}", str(session["fid"]))
        html = html.replace("{id_type}", "Faculty ID")
        html = html.replace("{total_students}", str(total_students))
        html = html.replace("{dept_students}", str(dept_students_count))
        html = html.replace("{attendance_percent}", str(attendance_percent))
        html = html.replace("{pending_tasks}", str(pending_tasks))
        return html

@app.route("/student-dashboard")
def student_dashboard():
    if "user_type" not in session or session["user_type"] != "student":
        return redirect("/")
    try:
        student = students.find_one({"sid": session["sid"]})
        if not student:
            return redirect("/")
        
        basic_completion = float(student.get("bc", 0))
        academic_completion = float(student.get("ac", 0))
        
        with open("student-dashboard.html", "r") as f:
            html = f.read()
            html = html.replace("{student_name}", student.get("sname", "Student"))
            html = html.replace("{username}", student.get("sname", "Student"))
            html = html.replace("{department}", student.get("dept", ""))
            html = html.replace("{sid}", str(session["sid"]))
            html = html.replace("{id_type}", "Student ID")
            html = html.replace("{batch}", student.get("ayear", ""))
            html = html.replace("{attendance_percent}", str(basic_completion))
            html = html.replace("{bc_attendance}", str(basic_completion))
            html = html.replace("{ac_attendance}", str(academic_completion))
            return html
    except Exception as e:
        print(f"Error loading dashboard: {str(e)}")
        return redirect("/")

@app.route("/student-basic")
def student_basic():
    if "user_type" not in session or session["user_type"] != "student":
        return redirect("/")
    try:
        student = students.find_one({"sid": session["sid"]})
        if not student:
            return redirect("/")
        
        profile_photo = student.get("photo_path")
        if profile_photo:
            photo_html = f'<img src="{profile_photo}" alt="Profile Photo">'
        else:
            photo_html = '<i class="ri-user-3-line"></i>'
        
        basic_completion = float(student.get("bc", 0))
        academic_completion = float(student.get("ac", 0))
        
        with open("studentBasic.html", "r") as f:
            html = f.read()
            html = html.replace("{username}", student.get("sname", "Student"))
            html = html.replace("{student_name}", student.get("sname", ""))
            html = html.replace("{department}", student.get("dept", ""))
            html = html.replace("{sid}", str(session["sid"]))
            html = html.replace("{id_type}", "Student ID")
            html = html.replace("{email}", student.get("email", "Not provided"))
            html = html.replace("{phone}", student.get("phone", "Not provided"))
            html = html.replace("{dob}", student.get("dob", "Not provided"))
            html = html.replace("{gender}", student.get("gender", "Not provided"))
            html = html.replace("{address1}", student.get("address1", "Not provided"))
            html = html.replace("{address2}", student.get("address2", "Not provided"))
            html = html.replace("{city}", student.get("city", "Not provided"))
            html = html.replace("{state}", student.get("state", "Not provided"))
            html = html.replace("{pincode}", student.get("pincode", "Not provided"))
            html = html.replace("{country}", student.get("country", "Not provided"))
            html = html.replace("{profile_photo}", photo_html)
            html = html.replace("{bc_completion}", str(basic_completion))
            html = html.replace("{ac_completion}", str(academic_completion))
            return html
    except Exception as e:
        print(f"Error loading student basic profile: {str(e)}")
        return redirect("/student-dashboard")

@app.route("/profile")
def profile():
    if "user_type" not in session or session["user_type"] != "student":
        return redirect("/")
    try:
        student = students.find_one({"sid": session["sid"]})
        if not student:
            return redirect("/")
        
        profile_photo = student.get("photo_path")
        if profile_photo:
            photo_html = f'<img src="{profile_photo}" alt="Profile Photo">'
        else:
            photo_html = '<i class="ri-user-3-line"></i>'
        
        academic_data = student.get("academic_records", [])
        if academic_data:
            academic_table = """
            <table>
                <thead>
                    <tr>
                        <th>Semester</th>
                        <th>Subject Code</th>
                        <th>Subject Name</th>
                        <th>Credits</th>
                        <th>Grade</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for record in academic_data:
                academic_table += f"""
                <tr>
                    <td>{record.get('semester', 'N/A')}</td>
                    <td>{record.get('subject_code', 'N/A')}</td>
                    <td>{record.get('subject_name', 'N/A')}</td>
                    <td>{record.get('credits', 'N/A')}</td>
                    <td>{record.get('grade', 'N/A')}</td>
                </tr>
                """
            
            academic_table += """
                </tbody>
            </table>
            """
        else:
            academic_table = '<div class="no-data">No academic records available</div>'
        
        exam_data = student.get("exam_records", [])
        if exam_data:
            exam_table = """
            <table>
                <thead>
                    <tr>
                        <th>Exam Name</th>
                        <th>Date</th>
                        <th>Subject</th>
                        <th>Marks Obtained</th>
                        <th>Total Marks</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for record in exam_data:
                status_class = "status-pass" if record.get("status") == "Pass" else "status-fail"
                exam_table += f"""
                <tr>
                    <td>{record.get('exam_name', 'N/A')}</td>
                    <td>{record.get('date', 'N/A')}</td>
                    <td>{record.get('subject', 'N/A')}</td>
                    <td>{record.get('marks_obtained', 'N/A')}</td>
                    <td>{record.get('total_marks', 'N/A')}</td>
                    <td><span class="status-chip {status_class}">{record.get('status', 'N/A')}</span></td>
                </tr>
                """
            
            exam_table += """
                </tbody>
            </table>
            """
        else:
            exam_table = '<div class="no-data">No exam records available</div>'
        
        upcoming_exams_data = student.get("upcoming_exams", [])
        if upcoming_exams_data:
            upcoming_exams = """
            <table>
                <thead>
                    <tr>
                        <th>Exam Name</th>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Subject</th>
                        <th>Room</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for exam in upcoming_exams_data:
                upcoming_exams += f"""
                <tr>
                    <td>{exam.get('exam_name', 'N/A')}</td>
                    <td>{exam.get('date', 'N/A')}</td>
                    <td>{exam.get('time', 'N/A')}</td>
                    <td>{exam.get('subject', 'N/A')}</td>
                    <td>{exam.get('room', 'N/A')}</td>
                </tr>
                """
            
            upcoming_exams += """
                </tbody>
            </table>
            """
        else:
            upcoming_exams = '<div class="no-data">No upcoming exams scheduled</div>'
            
        with open("profile.html", "r") as f:
            html = f.read()
            html = html.replace("{username}", student.get("sname", "Student"))
            html = html.replace("{student_name}", student.get("sname", ""))
            html = html.replace("{department}", student.get("dept", ""))
            html = html.replace("{sid}", str(session["sid"]))
            html = html.replace("{id_type}", "Student ID")
            html = html.replace("{batch}", student.get("ayear", ""))
            html = html.replace("{email}", student.get("email", "Not provided"))
            html = html.replace("{phone}", student.get("phone", "Not provided"))
            html = html.replace("{dob}", student.get("dob", "Not provided"))
            html = html.replace("{gender}", student.get("gender", "Not provided"))
            html = html.replace("{address1}", student.get("address1", "Not provided"))
            html = html.replace("{address2}", student.get("address2", "Not provided"))
            html = html.replace("{city}", student.get("city", "Not provided"))
            html = html.replace("{state}", student.get("state", "Not provided"))
            html = html.replace("{pincode}", student.get("pincode", "Not provided"))
            html = html.replace("{country}", student.get("country", "Not provided"))
            html = html.replace("{profile_photo}", photo_html)
            html = html.replace("{admission_year}", student.get("admission_year", "Not provided"))
            html = html.replace("{current_semester}", student.get("current_semester", "Not provided"))
            html = html.replace("{program}", student.get("program", "Not provided"))
            html = html.replace("{section}", student.get("section", "Not provided"))
            html = html.replace("{cgpa}", student.get("cgpa", "Not provided"))
            html = html.replace("{credits_earned}", student.get("credits_earned", "Not provided"))
            html = html.replace("{attendance_percent}", student.get("attendance_percent", "Not provided"))
            html = html.replace("{academic_table}", academic_table)
            html = html.replace("{exam_table}", exam_table)
            html = html.replace("{upcoming_exams}", upcoming_exams)
            return html
    except Exception as e:
        print(f"Error loading profile: {str(e)}")
        return redirect("/student-dashboard")

@app.route("/download-profile-pdf")
def download_profile_pdf():
    if "user_type" not in session or session["user_type"] != "student":
        return redirect("/")
    
    if not reportlab_available:
        return jsonify({"error": "PDF generation is not available. ReportLab library is missing."}), 500
    
    try:
        student = students.find_one({"sid": session["sid"]})
        if not student:
            return redirect("/")
        
        # Generate PDF filename
        pdf_filename = f"student_profile_{session['sid']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        
        # Create a BytesIO object to store the PDF in memory
        buffer = io.BytesIO()
        
        # Generate PDF directly with ReportLab
        generate_pdf_with_reportlab(buffer, student)
        
        # Reset buffer position to the beginning
        buffer.seek(0)
        
        # Return the PDF file
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=pdf_filename
        )
            
    except Exception as e:
        print(f"Unhandled error in download_profile_pdf: {str(e)}")
        traceback.print_exc()  # Print full traceback
        return jsonify({"error": "An unexpected error occurred while creating your PDF"}), 500

def generate_pdf_with_reportlab(buffer, student):
    """Generate a PDF document using ReportLab"""
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=6
    )
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#5469d4'),
        spaceAfter=6
    )
    normal_style = styles["Normal"]
    label_style = ParagraphStyle(
        'Label',
        parent=normal_style,
        fontSize=10,
        textColor=colors.gray
    )
    
    # Build the PDF content
    elements = []
    
    # Title
    elements.append(Paragraph("M.KUMARASAMY COLLEGE OF ENGINEERING", title_style))
    elements.append(Paragraph("Student Profile", subtitle_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Basic student info
    student_info = [
        [Paragraph(f"<b>Student Name:</b> {student.get('sname', 'Not provided')}", normal_style)],
        [Paragraph(f"<b>Student ID:</b> {student.get('sid', 'Not provided')}", normal_style)],
        [Paragraph(f"<b>Department:</b> {student.get('dept', 'Not provided')}", normal_style)]
    ]
    student_info_table = Table(student_info, colWidths=[450])
    student_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f7ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#5469d4')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(student_info_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Personal Information Section
    elements.append(Paragraph("Personal Information", section_title_style))
    
    personal_info_data = [
        [Paragraph("<b>Name:</b>", normal_style), 
         Paragraph(student.get("sname", "Not provided"), normal_style)],
        [Paragraph("<b>Email:</b>", normal_style), 
         Paragraph(student.get("email", "Not provided"), normal_style)],
        [Paragraph("<b>Phone:</b>", normal_style), 
         Paragraph(student.get("phone", "Not provided"), normal_style)],
        [Paragraph("<b>Date of Birth:</b>", normal_style), 
         Paragraph(student.get("dob", "Not provided"), normal_style)],
        [Paragraph("<b>Gender:</b>", normal_style), 
         Paragraph(student.get("gender", "Not provided"), normal_style)]
    ]
    
    personal_info_table = Table(personal_info_data, colWidths=[100, 350])
    personal_info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f7ff')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(personal_info_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Address Information
    elements.append(Paragraph("Address Information", section_title_style))
    
    address_data = [
        [Paragraph("<b>Address Line 1:</b>", normal_style), 
         Paragraph(student.get("address1", "Not provided"), normal_style)],
        [Paragraph("<b>Address Line 2:</b>", normal_style), 
         Paragraph(student.get("address2", "Not provided"), normal_style)],
        [Paragraph("<b>City:</b>", normal_style), 
         Paragraph(student.get("city", "Not provided"), normal_style)],
        [Paragraph("<b>State:</b>", normal_style), 
         Paragraph(student.get("state", "Not provided"), normal_style)],
        [Paragraph("<b>Pincode:</b>", normal_style), 
         Paragraph(student.get("pincode", "Not provided"), normal_style)],
        [Paragraph("<b>Country:</b>", normal_style), 
         Paragraph(student.get("country", "Not provided"), normal_style)]
    ]
    
    address_table = Table(address_data, colWidths=[100, 350])
    address_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f7ff')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(address_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Academic Information
    elements.append(Paragraph("Academic Information", section_title_style))
    
    academic_data = [
        [Paragraph("<b>Admission Year:</b>", normal_style), 
         Paragraph(student.get("admission_year", "Not provided"), normal_style)],
        [Paragraph("<b>Current Semester:</b>", normal_style), 
         Paragraph(student.get("current_semester", "Not provided"), normal_style)],
        [Paragraph("<b>Program:</b>", normal_style), 
         Paragraph(student.get("program", "Not provided"), normal_style)],
        [Paragraph("<b>Batch:</b>", normal_style), 
         Paragraph(student.get("ayear", "Not provided"), normal_style)],
        [Paragraph("<b>CGPA:</b>", normal_style), 
         Paragraph(student.get("cgpa", "Not provided"), normal_style)]
    ]
    
    academic_table = Table(academic_data, colWidths=[100, 350])
    academic_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f7ff')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(academic_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Add academic records if available
    academic_records = student.get("academic_records", [])
    if academic_records:
        elements.append(Paragraph("Academic Records", section_title_style))
        
        # Table header
        academic_table_data = [
            [
                Paragraph("<b>Semester</b>", normal_style),
                Paragraph("<b>Subject Code</b>", normal_style),
                Paragraph("<b>Subject Name</b>", normal_style),
                Paragraph("<b>Credits</b>", normal_style),
                Paragraph("<b>Grade</b>", normal_style)
            ]
        ]
        
        # Add data rows
        for record in academic_records:
            academic_table_data.append([
                Paragraph(record.get('semester', 'N/A'), normal_style),
                Paragraph(record.get('subject_code', 'N/A'), normal_style),
                Paragraph(record.get('subject_name', 'N/A'), normal_style),
                Paragraph(str(record.get('credits', 'N/A')), normal_style),
                Paragraph(record.get('grade', 'N/A'), normal_style)
            ])
        
        # Create table
        record_table = Table(academic_table_data, colWidths=[70, 80, 180, 50, 50])
        record_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5469d4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(record_table)
        elements.append(Spacer(1, 0.25*inch))
    
    # Add exam records if available
    exam_records = student.get("exam_records", [])
    if exam_records:
        elements.append(Paragraph("Examination Results", section_title_style))
        
        # Table header
        exam_table_data = [
            [
                Paragraph("<b>Exam Name</b>", normal_style),
                Paragraph("<b>Date</b>", normal_style),
                Paragraph("<b>Subject</b>", normal_style),
                Paragraph("<b>Marks</b>", normal_style),
                Paragraph("<b>Total</b>", normal_style),
                Paragraph("<b>Status</b>", normal_style)
            ]
        ]
        
        # Add data rows
        for record in exam_records:
            status = record.get('status', 'N/A')
            status_color = "green" if status == "Pass" else "red"
            
            exam_table_data.append([
                Paragraph(record.get('exam_name', 'N/A'), normal_style),
                Paragraph(record.get('date', 'N/A'), normal_style),
                Paragraph(record.get('subject', 'N/A'), normal_style),
                Paragraph(str(record.get('marks_obtained', 'N/A')), normal_style),
                Paragraph(str(record.get('total_marks', 'N/A')), normal_style),
                Paragraph(f'<font color="{status_color}">{status}</font>', normal_style)
            ])
        
        # Create table
        exam_record_table = Table(exam_table_data, colWidths=[80, 70, 120, 50, 50, 60])
        exam_record_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5469d4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(exam_record_table)
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"This document was generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(footer_text, styles["Italic"]))
    elements.append(Paragraph("M.Kumarasamy College of Engineering - Information Corner", 
                             ParagraphStyle('Footer', parent=styles["Italic"], alignment=TA_CENTER)))
    
    # Build the PDF
    doc.build(elements)

@app.route("/change-password", methods=["POST"])
def change_password():
    if "user_type" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 401
    data = request.json
    new_password = data.get("newPassword")
    try:
        if session["user_type"] == "student":
            collection = students
            id_field = "sid"
            id_value = session["sid"]
        else:
            collection = faculty
            id_field = "fid"
            id_value = session["fid"]
        collection.update_one({id_field: id_value}, {"$set": {"pass": new_password}})
        return jsonify({"status": "success", "message": "Password updated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to update password. Please try again."}), 500

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)