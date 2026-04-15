"""
Формы для работы с карточками и квизом.

Содержит формы для создания/редактирования карточек и форму для квиза,
а также валидацию вводимых данных.
"""

from django import forms
from .models import Card


# Форма для создания/редактирования карточки
class CardForm(forms.ModelForm):
    """
    Форма для создания и редактирования карточек слов.

    Основана на модели Card и включает поля word, translation, example.
    Содержит пользовательскую валидацию для полей word и translation.

    Attributes:
        Meta: Внутренний класс с метаданными формы.
    """

    class Meta:
        """
        Метаданные формы CardForm.

        Attributes:
            model: Модель, на которой основана форма.
            fields: Список полей модели, включаемых в форму.
            labels: Человекочитаемые названия полей.
        """
        model = Card
        fields = ['word', 'translation', 'example']
        labels = {
            'word': 'Слово',
            'translation': 'Перевод',
            'example': 'Пример использования (необязательно)',
        }

    def clean_word(self):
        """
        Валидация поля 'word'.

        Проверяет, что слово:
        - содержит минимум 2 символа
        - состоит только из букв (не содержит цифр или спецсимволов)

        Returns:
            str: Очищенное значение слова.

        Raises:
            forms.ValidationError: Если слово не проходит валидацию.
        """
        word = self.cleaned_data.get('word')
        if len(word) < 2:
            raise forms.ValidationError('Слово должно содержать минимум 2 символа')
        if not word.isalpha():
            raise forms.ValidationError('Слово должно состоять только из букв')
        return word

    def clean_translation(self):
        """
        Валидация поля 'translation'.

        Проверяет, что перевод содержит минимум 2 символа.

        Returns:
            str: Очищенное значение перевода.

        Raises:
            forms.ValidationError: Если перевод слишком короткий.
        """
        translation = self.cleaned_data.get('translation')
        if len(translation) < 2:
            raise forms.ValidationError('Перевод должен содержать минимум 2 символа')
        return translation


# Форма для квиза
class QuizForm(forms.Form):
    """
    Форма для проверки знаний в режиме квиза.

    Содержит поле для ввода ответа пользователя и скрытое поле
    для хранения индекса текущей карточки.

    Attributes:
        answer (CharField): Поле для ввода ответа пользователя.
        word_id (HiddenInput): Скрытое поле для хранения ID или индекса слова.
    """

    answer = forms.CharField(
        label='Ваш ответ',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Введите перевод...'})
    )

    word_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=True
    )

    def clean_answer(self):
        """
        Валидация поля 'answer'.

        Проверяет, что ответ не пустой и содержит хотя бы 1 символ
        после удаления пробелов.

        Returns:
            str: Очищенный ответ без лишних пробелов по краям.

        Raises:
            forms.ValidationError: Если ответ пустой.
        """
        answer = self.cleaned_data.get('answer')
        if len(answer.strip()) < 1:
            raise forms.ValidationError('Пожалуйста, введите ответ')
        return answer.strip()