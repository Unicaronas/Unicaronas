
  $.formUtils.addValidator({
    name: 'confirmation',
    validatorFunction: function (value, $el, config, language, $form) {
      var password,
        passwordInputName = $el.valAttr('confirm') ||
          ($el.attr('name') + '_confirmation'),
        $passwordInput = $form.find('[name="' + passwordInputName + '"]');
      if (!$passwordInput.length) {
        $.formUtils.warn('Password confirmation validator: could not find an input ' +
          'with name "' + passwordInputName + '"', true);
        return false;
      }

      password = $passwordInput.val();
      if (config.validateOnBlur && !$passwordInput[0].hasValidationCallback) {
        $passwordInput[0].hasValidationCallback = true;
        var keyUpCallback = function () {
          $el.validate();
        };
        $passwordInput.on('keyup', keyUpCallback);
        $form.one('formValidationSetup', function () {
          $passwordInput[0].hasValidationCallback = false;
          $passwordInput.off('keyup', keyUpCallback);
        });
      }

      return value === password;
    },
    errorMessage: '',
    errorMessageKey: 'notConfirmed'
  });

  /*
   * Validate password strength
   */
  $.formUtils.addValidator({
    name: 'strength',
    validatorFunction: function (val, $el) {
      var requiredStrength = $el.valAttr('strength') || 2;
      if (requiredStrength && requiredStrength > 3) {
        requiredStrength = 3;
      }

      return $.formUtils.validators.validate_strength.calculatePasswordStrength(val) >= requiredStrength;
    },
    errorMessage: '',
    errorMessageKey: 'badStrength',

    /**
     * Code more or less borrowed from jQuery plugin "Password Strength Meter"
     * written by Darren Mason (djmason9@gmail.com), myPocket technologies (www.mypocket-technologies.com)
     * @param {String} password
     * @return {Number}
     */
    calculatePasswordStrength: function (password) {

      if (password.length < 4) {
        return 0;
      }

      var score = 0;

      var checkRepetition = function (pLen, str) {
        var res = '';
        for (var i = 0; i < str.length; i++) {
          var repeated = true;

          for (var j = 0; j < pLen && (j + i + pLen) < str.length; j++) {
            repeated = repeated && (str.charAt(j + i) === str.charAt(j + i + pLen));
          }
          if (j < pLen) {
            repeated = false;
          }
          if (repeated) {
            i += pLen - 1;
            repeated = false;
          }
          else {
            res += str.charAt(i);
          }
        }
        return res;
      };

      //password length
      score += password.length * 4;
      score += ( checkRepetition(1, password).length - password.length ) * 1;
      score += ( checkRepetition(2, password).length - password.length ) * 1;
      score += ( checkRepetition(3, password).length - password.length ) * 1;
      score += ( checkRepetition(4, password).length - password.length ) * 1;

      //password has 3 numbers
      if (password.match(/(.*[0-9].*[0-9].*[0-9])/)) {
        score += 5;
      }

      //password has 2 symbols
      if (password.match(/(.*[!,@,#,$,%,^,&,*,?,_,~].*[!,@,#,$,%,^,&,*,?,_,~])/)) {
        score += 5;
      }

      //password has Upper and Lower chars
      if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) {
        score += 10;
      }

      //password has number and chars
      if (password.match(/([a-zA-Z])/) && password.match(/([0-9])/)) {
        score += 15;
      }
      //
      //password has number and symbol
      if (password.match(/([!,@,#,$,%,^,&,*,?,_,~])/) && password.match(/([0-9])/)) {
        score += 15;
      }

      //password has char and symbol
      if (password.match(/([!,@,#,$,%,^,&,*,?,_,~])/) && password.match(/([a-zA-Z])/)) {
        score += 15;
      }

      //password is just a numbers or chars
      if (password.match(/^\w+$/) || password.match(/^\d+$/)) {
        score -= 10;
      }

      //verifying 0 < score < 100
      if (score < 0) {
        score = 0;
      }
      if (score > 100) {
        score = 100;
      }

      if (score < 20) {
        return 0;
      }
      else if (score < 40) {
        return 1;
      }
      else if (score <= 60) {
        return 2;
      }
      else {
        return 3;
      }
    },

    strengthDisplay: function ($el, options) {
      var config = {
        fontSize: '12pt',
        padding: '4px',
        bad: 'Very bad',
        weak: 'Weak',
        good: 'Good',
        strong: 'Strong'
      };

      if (options) {
        $.extend(config, options);
      }

      $el.bind('keyup', function () {
        var val = $(this).val(),
          $parent = typeof config.parent === 'undefined' ? $(this).parent() : $(config.parent),
          $displayContainer = $parent.find('.strength-meter'),
          strength = $.formUtils.validators.validate_strength.calculatePasswordStrength(val),
          css = {
            background: 'pink',
            color: '#FF0000',
            fontWeight: 'bold',
            border: 'red solid 1px',
            borderWidth: '0px 0px 4px',
            display: 'inline-block',
            fontSize: config.fontSize,
            padding: config.padding
          },
          text = config.bad;

        if ($displayContainer.length === 0) {
          $displayContainer = $('<span></span>');
          $displayContainer
            .addClass('strength-meter')
            .appendTo($parent);
        }

        if (!val) {
          $displayContainer.hide();
        } else {
          $displayContainer.show();
        }

        if (strength === 1) {
          text = config.weak;
        }
        else if (strength === 2) {
          css.background = 'lightyellow';
          css.borderColor = 'yellow';
          css.color = 'goldenrod';
          text = config.good;
        }
        else if (strength >= 3) {
          css.background = 'lightgreen';
          css.borderColor = 'darkgreen';
          css.color = 'darkgreen';
          text = config.strong;
        }

        $displayContainer
          .css(css)
          .text(text);
      });
    }
  });
