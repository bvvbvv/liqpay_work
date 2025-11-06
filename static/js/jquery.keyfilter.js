/*!
 * jQuery KeyFilter Plugin
 * Simplified version by Allan Jardine / adapted for modern jQuery (2024)
 * License: MIT
 */
(function ($) {
  $.fn.keyfilter = function (input) {
    return this.each(function () {
      var $this = $(this);
      var regex = null;

      // predefined filters
      var presets = {
        numeric: /[0-9]/,
        integer: /[0-9\-]/,
        float: /[0-9\.]/,
        hex: /[0-9A-Fa-f]/,
        alpha: /[A-Za-zА-Яа-яЁёЇїІіЄє]/,
        alpha_s: /[A-Za-zА-Яа-яЁёЇїІіЄє\s]/,
        alphanum: /[A-Za-z0-9А-Яа-яЁёЇїІіЄє]/,
        email: /[A-Za-z0-9_\.\-\+@]/,
        phone: /[0-9\-\+\(\)\s]/,
      };

      if (typeof input === 'string' && presets[input]) {
        regex = presets[input];
      } else if (input instanceof RegExp) {
        regex = input;
      } else {
        console.error('keyfilter: invalid argument');
        return;
      }

      // filter by keypress
      $this.on('keypress keydown', function (e) {
        if (e.ctrlKey || e.altKey || e.metaKey) return;
        var ch = e.key;
        if (ch && ch.length === 1 && !regex.test(ch)) {
          e.preventDefault();
        }
      });

      // sanitize pasted content
      $this.on('input', function () {
        var v = $this.val();
        $this.val(v.split('').filter(c => regex.test(c)).join(''));
      });
    });
  };
})(jQuery);
