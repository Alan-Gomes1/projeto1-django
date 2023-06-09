from unittest import TestCase

from django.test import TestCase as DjangoTestCase
from django.urls import reverse
from parameterized import parameterized

from authors.forms import RegisterForm


class AuthorRegisterFormUnitTest(TestCase):
    @parameterized.expand([
        ('username', 'Your username'),
        ('email', 'Your e-mail'),
        ('first_name', 'Ex.: John'),
        ('last_name', 'Ex.: Doe'),
        ('password', 'Type your password here'),
        ('confirm_password', 'Repeat your password'),
    ])
    def test_fields_placeholder(self, field, placeholder):
        form = RegisterForm()
        current_placeholder = form[field].field.widget.attrs['placeholder']
        self.assertEqual(current_placeholder, placeholder)

    @parameterized.expand([
        ('username', 'Mandatory. Minimum 4 and maximum 150 characters.\
        Only letters, numbers and @/./+/-/_.'),

        ('password', """
        Password must have at least one uppercase letter,
        one lowercase letter and one number. The length should be
        at last 8 characters.
        """),
    ])
    def test_fields_help_text(self, field, needed):
        form = RegisterForm()
        current = form[field].field.help_text
        self.assertEqual(current, needed)

    @parameterized.expand([
        ('username', 'Username'),
        ('first_name', 'First name'),
        ('last_name', 'Last name'),
        ('email', 'E-mail'),
        ('password', 'Password'),
        ('confirm_password', 'Confirm password'),
    ])
    def test_fields_label(self, field, needed):
        form = RegisterForm()
        current = form[field].field.label
        self.assertEqual(current, needed)


class AuthorRegisterFormIntegrationTest(DjangoTestCase):
    def setUp(self):
        self.form_data = {
            'username': 'user',
            'first_name': 'first',
            'last_name': 'last',
            'email': 'email@anyemail.com',
            'password': 'Str0ngP@ssword1',
            'confirm_password': 'Str0ngP@ssword1',
        }
        self.form = RegisterForm(data=self.form_data)

    @parameterized.expand([
        ('username', 'This field is required'),
        ('first_name', 'Write your first name'),
        ('last_name', 'Write your last name'),
        ('password', 'Password must not be empty'),
        ('confirm_password', 'This field is required'),
        ('email', 'This field is required'),
    ])
    def test_fields_cannot_be_empty(self, field, msg):
        self.form_data[field] = ''
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get(field))

    def test_username_field_min_length_should_be_4(self):
        self.form_data['username'] = 'Leo'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Make sure the value is at least 4 characters long.'
        self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('username'))

    def test_username_field_max_length_should_be_150(self):
        self.form_data['username'] = 'A' * 151
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Username must have less than 150 characters.'
        self.assertIn(msg, response.context['form'].errors.get('username'))
        self.assertIn(msg, response.content.decode('utf-8'))

    def test_password_field_have_lower_upper_case_letters_and_numbers(self):
        self.form_data['password'] = 'abc123'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = ("""
            Password must have at least one uppercase letter,
            one lowercase letter and one number. The length should be
            at last 8 characters.""")
        self.assertIn(msg, response.context['form'].errors.get('password'))
        self.assertIn(msg, response.content.decode('utf-8'))

        self.form_data['password'] = '@Abc123.'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)
        self.assertNotIn(msg, response.content.decode('utf-8'))

    def test_password_and_confirm_password_are_equal(self):
        self.form_data['password'] = '@Abc123.'
        self.form_data['confirm_password'] = '@Abc123.'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Password and confirm password must be equal'
        self.assertNotIn(msg, response.content.decode('utf-8'))

    def test_password_and_confirm_password_are_different(self):
        self.form_data['password'] = '@Abc123.'
        self.form_data['confirm_password'] = '@Abc123.4'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Password and confirm password must be equal'
        self.assertIn(msg, response.context['form'].errors.get(
            'confirm_password'
        ))
        self.assertIn(msg, response.content.decode('utf-8'))

    def test_send_get_request_to_registration_create_view_returns_404(self):
        url = reverse('authors:register_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_form_validation(self):
        self.assertTrue(self.form.is_valid())

    def test_email_field_must_be_unique(self):
        url = reverse('authors:register_create')
        self.client.post(url, data=self.form_data, follow=True)
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Email already exists'
        self.assertIn(msg, response.context['form'].errors.get('email'))
        self.assertIn(msg, response.content.decode('utf-8'))

    def test_author_created_can_login(self):
        url = reverse('authors:register_create')
        self.form_data.update({
            'username': 'testuser',
            'password': '@Bc123456',
            'confirm_password': '@Bc123456',
        })

        self.client.post(url, data=self.form_data, follow=True)
        is_authenticated = self.client.login(
            username='testuser',
            password='@Bc123456',
        )
        self.assertTrue(is_authenticated)
