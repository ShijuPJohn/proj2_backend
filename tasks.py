import datetime
import logging
import time
from datetime import datetime as dt

from celery import shared_task
from flask import current_app, render_template
from flask_mail import Message, Mail
from sqlalchemy import func

from models.models import Issue, db, Section, EBook, Request, User

logger = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def celery_test(x, y):
    print("celery test invoked")
    time.sleep(1)
    return x + y


@shared_task(ignore_result=False)
def test_mail():
    app = current_app._get_current_object()
    mail = Mail(app)
    msg = Message(
        'Test Email',
        recipients=["spjohnninth@gmail.com"],
        body='Testing email'
    )

    mail.send(msg)
    return 'Email sent successfully!'


@shared_task(ignore_result=False)
def triggered_async_job():
    filename = str(dt.now()) + '.csv'
    file_path = f"static/reports/{filename}"
    file = open(file_path, 'w')
    file.write(
        "issue_id,book_title,book_authors,book_sections,issued_to_user_id,issued_to_user_name,book_issued,book_returned\n")
    issues = Issue.query.all()
    for issue in issues:
        book_authors_line = '|'.join([author.name for author in issue.book.authors])
        book_sections_line = '|'.join([section.name for section in issue.book.sections])
        line_for_issue = f"{issue.id},{issue.book.title},{book_authors_line},{book_sections_line},{issue.user.id},{issue.user.username}{issue.date_time_issued},{issue.date_time_returned}\n"
        file.write(line_for_issue)
    file.close()
    app = current_app._get_current_object()
    mail = Mail(app)
    msg = Message(
        'CSV Report file',
        recipients=["spjohnninth@gmail.com"],
        body='Attached the csv report file.'
    )
    with open(file_path, 'rb') as fp:
        msg.attach(
            filename=filename,
            content_type="text/csv",
            data=fp.read()
        )
        mail.send(msg)
    return 'csv file written'


@shared_task(ignore_result=False)
def celery_beat():
    return "Hey! there!"


@shared_task(ignore_result=False)
def get_monthly_stats():
    thirty_days_ago = dt.utcnow() - datetime.timedelta(days=30)

    new_users_count = User.query.filter(User.date_time_created >= thirty_days_ago).count()

    total_requests_count = Request.query.count()

    rejected_requests_count = Request.query.filter(Request.status == 'rejected').count()

    total_issues_count = Issue.query.count()

    books_per_section = db.session.query(
        Section.name, func.count(EBook.id)
    ).outerjoin(Section.books).group_by(Section.id).all()

    top_books = db.session.query(
        EBook.title,
        func.count(Request.id).label('request_count')
    ).outerjoin(Request).group_by(EBook.id).order_by(func.count(Request.id).desc()).limit(5).all()

    html_report = render_template("report.html", new_users_count=new_users_count,
                                  total_requests_count=total_requests_count, total_issues_count=total_issues_count,
                                  books_per_section={section: count for section, count in books_per_section},
                                  top_books=[{'title': book.title, 'request_count': book.request_count} for book in
                                             top_books])
    app = current_app._get_current_object()
    mail = Mail(app)
    msg = Message(
        'Monthly Report',
        recipients=["spjohnninth@gmail.com"],
        html=html_report
    )
    mail.send(msg)
    return 'Report sent'

# return {
#     'new_users_count': new_users_count,
#     'total_requests_count': total_requests_count,
#     'rejected_requests_count': rejected_requests_count,
#     'total_issues_count': total_issues_count,
#     'books_per_section': {section: count for section, count in books_per_section},
#     'top_books': [{'title': book.title, 'request_count': book.request_count} for book in top_books]
# }
