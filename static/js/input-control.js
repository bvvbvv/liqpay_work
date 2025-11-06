/*!
 * Input Control + KeyFilter Integration
 * Автоматическая фильтрация и валидация input-полей по data-атрибутам
 * Поддерживает keyfilter.js (если подключён)
 */

$(function () {

  // --------------------------
  // Подключение keyfilter (если плагин есть)
  // --------------------------
  function applyKeyFilter($input) {
    if (!$.fn.keyfilter) return;

    let type = $input.data('type');
    switch (type) {
      case 'number':
        $input.keyfilter('numeric');
        break;
      case 'letters':
        $input.keyfilter('alpha');
        break;
      case 'email':
        $input.keyfilter('email');
        break;
      case 'phone':
        $input.keyfilter('phone');
        break;
    }
  }

  // --------------------------
  // Основная валидация поля
  // --------------------------
  function validateField($input) {
    let type = $input.data('type');
    let val = $input.val().trim();
    let valid = true;

    // --- Фильтрация (дополнительно, для надёжности) ---
    if (type === 'number') {
      $input.val(val.replace(/[^0-9]/g, ''));
    }
    if (type === 'letters') {
      $input.val(val.replace(/[^a-zA-Zа-яА-Яїієё]/g, ''));
    }

    // --- Проверка по шаблону ---
    if (type === 'email' && val) {
      valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
    }
    if (type === 'phone' && val) {
      valid = /^\+?\d[\d\-\s()]{7,20}$/.test(val);
    }

    // --- Проверка диапазона ---
    let min = parseInt($input.data('min'));
    let max = parseInt($input.data('max'));
    if (type === 'number' && val) {
      let num = parseInt(val);
      if ((min && num < min) || (max && num > max)) valid = false;
    }

    // --- Проверка обязательности ---
    if ($input.prop('required') && !val) valid = false;

    // --- Подсветка ошибок ---
    $input.toggleClass('error', !valid);
    return valid;
  }

  // --------------------------
  // Инициализация всех полей
  // --------------------------
  $('input[data-type]').each(function () {
    let $input = $(this);
    applyKeyFilter($input);
  });

  // --------------------------
  // Валидация при вводе
  // --------------------------
  $(document).on('input blur change', 'input[data-type]', function () {
    validateField($(this));
  });

  // --------------------------
  // Проверка формы перед submit
  // --------------------------
  $(document).on('submit', 'form', function (e) {
    let ok = true;
    $(this).find('input[data-type], input[required]').each(function () {
      if (!validateField($(this))) ok = false;
    });
    if (!ok) {
      e.preventDefault();
      alert('Пожалуйста, исправьте ошибки в форме.');
    }
  });

});
