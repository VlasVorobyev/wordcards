"""
Представления (views) для приложения cards.

Содержит все обработчики запросов:
- список карточек с сортировкой
- детальный просмотр
- создание и редактирование
- квиз для проверки знаний
"""

import random
from django.shortcuts import render, redirect, get_object_or_404
from .models import Card
from .forms import CardForm, QuizForm


# Страница со списком всех карточек
def card_list(request):
    """
    Отображает список всех карточек с возможностью сортировки.

    Поддерживает сортировку по:
    - слову (А-Я и Я-А)
    - переводу (А-Я и Я-А)
    - дате создания (новые/старые сначала)
    - случайному порядку

    Args:
        request (HttpRequest): HTTP-запрос с параметром 'sort' в GET.

    Returns:
        HttpResponse: Отрендеренный шаблон card_list.html с контекстом,
                      содержащим список карточек, текущий способ сортировки
                      и общее количество карточек.
    """
    # Получаем параметр сортировки из URL (по умолчанию - новые сначала)
    sort_by = request.GET.get('sort', '-created_at')

    # Базовый запрос
    cards = Card.objects.all()

    # Словарь с вариантами сортировки
    sort_options = {
        'word_asc': 'word',  # слово А-Я
        'word_desc': '-word',  # слово Я-А
        'trans_asc': 'translation',  # перевод А-Я
        'trans_desc': '-translation',  # перевод Я-А
        'date_asc': 'created_at',  # старые сначала
        'date_desc': '-created_at',  # новые сначала
        'random': '?',  # случайный порядок
    }

    # Применяем сортировку, если она существует
    if sort_by in sort_options:
        cards = cards.order_by(sort_options[sort_by])
    else:
        cards = cards.order_by('-created_at')  # по умолчанию

    # Передаём в шаблон текущий способ сортировки
    context = {
        'cards': cards,
        'current_sort': sort_by,
        'total_count': cards.count(),
    }

    return render(request, 'cards/card_list.html', context)


# Страница с деталями одной карточки
def card_detail(request, pk):
    """
    Отображает детальную информацию о конкретной карточке.

    Args:
        request (HttpRequest): HTTP-запрос.
        pk (int): Первичный ключ (ID) карточки.

    Returns:
        HttpResponse: Отрендеренный шаблон card_detail.html с данными карточки.

    Raises:
        Http404: Если карточка с указанным pk не найдена.
    """
    card = get_object_or_404(Card, pk=pk)  # если не найдено — ошибка 404
    return render(request, 'cards/card_detail.html', {'card': card})


# Создание новой карточки
def card_create(request):
    """
    Обрабатывает создание новой карточки.

    При GET-запросе отображает пустую форму.
    При POST-запросе проверяет валидность данных и сохраняет карточку.

    Args:
        request (HttpRequest): HTTP-запрос (GET или POST).

    Returns:
        HttpResponse: 
            - При GET: страница с формой создания.
            - При POST с ошибками: страница с формой и сообщениями об ошибках.
            - При успешном POST: редирект на список карточек.
    """
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cards:card_list')
    else:
        form = CardForm()

    return render(request, 'cards/card_create.html', {'form': form})


# Редактирование карточки
def card_update(request, pk):
    """
    Обрабатывает редактирование существующей карточки.

    При GET-запросе отображает форму с заполненными данными карточки.
    При POST-запросе проверяет валидность и сохраняет изменения.

    Args:
        request (HttpRequest): HTTP-запрос (GET или POST).
        pk (int): Первичный ключ редактируемой карточки.

    Returns:
        HttpResponse:
            - При GET: страница с формой редактирования.
            - При POST с ошибками: страница с формой и сообщениями.
            - При успешном POST: редирект на страницу деталей карточки.

    Raises:
        Http404: Если карточка с указанным pk не найдена.
    """
    card = get_object_or_404(Card, pk=pk)

    if request.method == 'POST':
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            return redirect('cards:card_detail', pk=card.pk)
    else:
        form = CardForm(instance=card)

    return render(request, 'cards/card_update.html', {'form': form, 'card': card})


# Квиз — случайная карточка и проверка ответа
def quiz(request):
    """
    Обрабатывает квиз для проверки знаний слов.

    При GET-запросе показывает случайную карточку и форму для ответа.
    При POST-запросе проверяет ответ пользователя и показывает результат.

    Особенности:
    - Если карточек нет, показывает сообщение об ошибке.
    - Сохраняет индекс текущей карточки в скрытом поле формы.
    - При правильном ответе показывает пример использования слова.

    Args:
        request (HttpRequest): HTTP-запрос (GET или POST).

    Returns:
        HttpResponse:
            - Если нет карточек: страница с сообщением об ошибке.
            - При GET: страница со случайной карточкой и формой.
            - При POST: страница с результатом проверки.
    """
    cards = list(Card.objects.all())

    if not cards:
        return render(request, 'cards/quiz.html',
                      {'error': 'Нет карточек. Сначала добавьте карточки!'})

    card_index = random.randint(0, len(cards) - 1)
    random_card = cards[card_index]
    result = None

    if request.method == 'POST':
        # Обработка ответа пользователя
        form = QuizForm(request.POST)
        if form.is_valid():
            # Получаем индекс карточки из скрытого поля
            card_index = int(form.cleaned_data['word_id'])
            random_card = cards[card_index]

            answer = form.cleaned_data['answer'].lower()
            correct_translation = random_card.translation.lower()

            if answer == correct_translation:
                result = (f"✅ Правильно! «{random_card.word}» — это {random_card.translation}. "
                          f"(Пример: {random_card.example})")
            else:
                result = (f"❌ Неправильно. «{random_card.word}» "
                          f"переводится как «{random_card.translation}»")
    else:
        # GET-запрос: выбираем случайную карточку
        card_index = random.randint(0, len(cards) - 1)
        random_card = cards[card_index]
        form = QuizForm(initial={'word_id': card_index})

    return render(request, 'cards/quiz.html', {
        'form': form,
        'card': random_card,
        'card_index': card_index,
        'result': result,
    })