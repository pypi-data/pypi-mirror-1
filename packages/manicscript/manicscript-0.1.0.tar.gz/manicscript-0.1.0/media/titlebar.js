
MCESG.widgets.TitleBar = {
        tbflash: undefined,
        messages: 0,

        markTitlebar: function (nm) {
            this.messages += nm;

            if( nm == 0 ) this.resetTitlebar();
            else {
                    this.flashTbOn();
            }
        },

        flashTbOn: function () {
            this.unMarkTitlebar();
            document.title = '[ ' + this.messages + ' ] ' + document.title;
            clearTimeout(this.tbflash);
            this.tbflash = setTimeout('MCESG.widgets.TitleBar.flashTbOff()', 500);
        },

        flashTbOff: function () {
            this.unMarkTitlebar();
            document.title = '[   ] ' + document.title;
            clearTimeout(this.tbflash);
            this.tbflash = setTimeout('MCESG.widgets.TitleBar.flashTbOn()', 1000);
        },

        unMarkTitlebar: function () {
            document.title = document.title.replace(/^\[.*\] /, '');
        },

        no_op: function () { ; },

        resetTitlebar: function () {
            clearTimeout(MCESG.widgets.TitleBar.tbflash);
            MCESG.widgets.TitleBar.unMarkTitlebar();
            MCESG.widgets.TitleBar.messages = 0;
        }
};
