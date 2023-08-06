$Id: README.txt 1111 2007-06-12 19:42:00Z azaretsky $

Как использовать продукт mailtemplate:

    Модуль ks.lib.mailtemplate.mailtemplate содержит функцию

        template(use_container, use_alternative,
                 charset, mime, filename,
                 mail_header, mail_body, mail_footer,
                 text_headers, address_headers,
                 data)

    use_container, use_alternative -- bool

    mail_header, mail_body, mail_footer --
        форматные строки (ключи берутся из параметра data)

    text_headers -- dict заголовков с текстом (например, 'Subject')

    address_headers -- dict заголовков с адресами (например, 'From','To','Reply-To')


    Модуль также содержит стартовый код для тестирования функции из командной строки::

        python mailtemplate.py <имя>=<значение> ...

    Из параметров с именами text_* собирается text_headers, из address_* -- address_headers,
    из data_* -- data.
    Если указан параметр -sendmail, его значение используется, как строка
    для запуска внешней программы, на стандартный ввод которой будет передан
    сформированный текст. Если параметр не указан, текст пишется в stdout.

    Пример::

        python mailtemplate.py use_container=True text_Subject='qq%(body)s' \
             address_Reply-To=test@test.tld charset=utf8 \
             mail_header="<html><body>мама мыла раму</body></html>" address_To='test <a@b.c>' \
             data_body=somebody mail_body='%(body)s|%(body)s' mime=text/html \
             -sendmail='/usr/sbin/sendmail -f test@ureach.com test@ureach.com'
