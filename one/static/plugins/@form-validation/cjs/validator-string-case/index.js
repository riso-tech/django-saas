'use strict';

/**
 * FormValidation (https://formvalidation.io)
 * The best validation library for JavaScript
 * (c) 2013 - 2023 Nguyen Huu Phuoc <me@phuoc.ng>
 */
function stringCase() {
    return {
        /**
         * Check if a string is a lower or upper case one
         */
        validate: function (input) {
            if (input.value === '') {
                return { valid: true };
            }
            var opts = Object.assign({}, { case: 'lower' }, input.options);
            var caseOpt = (opts.case || 'lower').toLowerCase();
            return {
                message: opts.message ||
                    (input.l10n
                        ? 'upper' === caseOpt
                            ? input.l10n.stringCase.upper
                            : input.l10n.stringCase.default
                        : opts.message),
                valid: 'upper' === caseOpt
                    ? input.value === input.value.toUpperCase()
                    : input.value === input.value.toLowerCase(),
            };
        },
    };
}

exports.stringCase = stringCase;
