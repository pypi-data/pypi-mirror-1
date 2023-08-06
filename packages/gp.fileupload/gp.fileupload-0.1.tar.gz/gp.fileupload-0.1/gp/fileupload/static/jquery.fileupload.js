/* file upload progress bar */
if (typeof($)!='undefined') {

var FileUploadRegistry = {
    wrappers: new Array(),
    forms: {},
};

(function($) {

$.fn.fileUpload = function(options) {

    // default settings
    var settings = $.extend({
        add_link: true,
        link_label: 'Add more files...',
        add_submit: true,
        submit_label: 'Send files',
        field_name: 'file',
        submit_empty_forms: true,
        use_iframes: true,
        stat_url: '/gp.fileupload.stat/',
        stat_delay: 200,
        stat_timeout: 1500,
        success: function() {},
        error: function() {},
        action: window.location.href.split('#')[0].split('?')[0]
    }, options);

    var Wrapper = function(element) {
        // Wrapper class
        this.element = element;
        this.settings = settings;
        this.forms = new Array();
        this.forms_wrapper = $('<div></div>')
                                .appendTo(element);
    }
    $.extend(Wrapper.prototype, {
        // Wrapper methods
        initialize: function() {
            var self = this;
            var empty = true;
            $('form', this.element).each(function() {
                if (!$(this).hasClass('fuForm'))
                    self.forms.push(new Form(this, self));
                else
                    empty = false;
            });
            if (empty && self.forms.length == 0) {
                // show form
                self.showNext();

                // add other link
                if (settings.add_link == true) {
                    var label = settings.link_label;
                    $('<a href="#" class="fuNext">'+label+'</a>')
                        .appendTo(self.element)
                        .wrap('<div class="fuNextWrapper"></div>')
                        .click(function() { self.showNext() });
                }

                // add submit
                $('<input class="fuButton" type="submit" />')
                    .appendTo(self.element)
                    .attr('value', self.settings.submit_label)
                    .click(function() {
                        self.submit();
                    });
            }
        },
        showNext: function() {
            var value = '' +
                '<form class="fuForm" method="POST" ' +
                      'enctype="multipart/form-data" ' +
                      'action="'+this.settings.action+'"> ' +
                    '<input type="file" ' +
                           'name="'+this.settings.field_name+'" />' +
                '</form>';
            var form = $(value).appendTo(this.forms_wrapper);
            this.forms.push(new Form(form, this));
        },
        submit: function() {
            var self = this;

            $('.fuButton', self.element).css('display', 'none');
            $('.fuNext', self.element).css('display', 'none');

            $(self.forms).each(function(i, item) {
                var form = item.form

                // hide form
                $(form).css('display','none');

                // check filenames
                var filenames = '';
                $('input:file', form).each(function() {
                    var filename = $(this).attr('value');
                    if (filename) {
                        // clean filename
                        if (filename.match('/'))
                            // unix path
                            filename = filename.split('/').pop();
                        if (filename.match('\\\\'))
                            // windows path
                            filename = filename.split('\\').pop();

                        // concat
                        if (filenames != '') {
                            filenames += ' - '+filename;
                        } else {
                            filenames = filename;
                        }
                    }
                });

                if (filenames) {
                    // show progress bar and change target only if we have some files

                    // add progress bar
                    var progress = '' +
                        '<div class="fuWrapper">' +
                            '<span>'+filenames+'</span>' +
                            '<div style="position:relative">' +
                                '<span style="float:left;" ' +
                                      'class="fuProgress">&nbsp;</span><br />' +
                            '</div></div>';
                    progress = $(progress).appendTo(item.wrapper.element);
                    item.progress = $('.fuProgress', progress);

                    if (self.settings.use_iframes) {
                        // add iframe
                        var target = '<iframe style="display:none" ' +
                                             'name="iframe_'+item.id+'">' +
                                     '</iframe>';
                        $(target).appendTo(item.wrapper.element);

                        // change target
                        $(form).attr('target', 'iframe_'+item.id);
                    }

                } else {
                    if (!self.settings.submit_empty_forms)
                        // dont submit empty form
                        item.submit = false;
                }
            });
            self.submitNext()
        },
        submitNext: function() {
            if (this.forms.length > 0) {
                var item = this.forms.shift();
                if (item.submit) {
                    item.form.submit();
                    item.setTimeout(1500);
                } else {
                    this.submitNext();
                }
            } else {
                this.settings.success();
            }
        },
    });

    var Form = function(form, wrapper) {
        // Form class
        var id = ''+Math.random()*10000000000000000000;
        this.id = id;
        this.submit = true;
        this.retries = 0;
        this.form = form;
        this.wrapper = wrapper
        this.progress = null;

        // register form
        FileUploadRegistry.forms[id] = this;

        // add session to form action
        var action = $(form).attr('action')+'?gp.fileupload.id='+id;

        // set form attributes
        $(form)
            .addClass('fuForm')
            .attr('id', id)
            .attr('action', action)
            .attr('method', 'POST')
            .attr('enctype', 'multipart/form-data')
            .wrap('<div></div>');

        // bind click on existing form
        $('input[type^="submit"]', form)
            .addClass('fuButton')
            .click(function() { wrapper.submit() });
    }
    $.extend(Form.prototype, {
        // Form methods
        setTimeout: function(delay) {
            if (!delay)
                delay = this.wrapper.settings.stat_delay;
            setTimeout('FileUploadRegistry.forms["'+this.id+'"].stat()', delay);
        },
        stat: function() {
            // get stats for a session
            var self = this;
            $.ajax({
                 type: 'POST',
                 dataType: 'json',
                 timeout: self.wrapper.settings.stat_timeout,
                 url: self.wrapper.settings.stat_url+self.id,
                 success: function(response) {
                        if (response.state == -1) {
                            // upload failure
                            self.progress.css('width','100%')
                                         .addClass('fuProgressFailure')
                                         .html('&nbsp;');
                            self.wrapper.submitNext()
                            return;
                        }
                        if (response.state == 0) {
                            // not started
                            self.retries += 1;
                            if (self.retries > 3) {
                                self.progress.css('width','100%')
                                             .addClass('fuProgressFailure')
                                             .html('&nbsp;');
                                self.wrapper.submitNext();
                            } else {
                                self.setTimeout(1500);
                            }
                            return;
                        } else {
                            self.retries = 0;
                        }
                        if (response.percent >= 0 && response.percent < 100) {
                            // progress
                            self.progress.css('width',response.percent+'%')
                                         .html(response.percent+'%');
                            self.setTimeout();
                        }
                        if (response.percent == 100) {
                            // upload success
                            self.progress.css('width','100%')
                                         .addClass('fuProgressSuccess')
                                         .html(response.percent+'%')
                                         .removeClass('fuProgress');
                            self.wrapper.submitNext()
                        }
                 },
                 error: function(response) {
                     self.retries += 1;
                     self.setTimeout(1500);
                 }
            }); 
        }
    })
    return this.each(function(i, item) {
        if ($(item).attr('enctype') == 'multipart/form-data')
            // we have an existing form so wrap it
            item = $(item).wrap('<div></div>').parent()
        var wrapper = new Wrapper(item);
        wrapper.initialize()
        FileUploadRegistry.wrappers.push(wrapper);
    });
}

})(jQuery);

}
