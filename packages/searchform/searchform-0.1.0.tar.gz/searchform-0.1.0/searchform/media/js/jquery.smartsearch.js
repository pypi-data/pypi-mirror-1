/* Search functions for the search form */

(function ($) {

    /* This plugin convert a simple multi select box into a full
       featured double select with buttons to move items around
       between both selects */
    $.fn.easySelect = function () {

        return this.each(function () {
                var name = $(this).attr("name").split("__")[0];
                var size = $(this).attr("size");
                var select_all = "<button class='select-all-action'>Seleccionar todo</button>";
                var add_remove = "<div class='add-remove-buttons'>"
                                 + "<button class='add'>Añadir</button>"
                                 + "<button class='delete'>Borrar</button>"
                                 + "</div>";
                var selected = "<div class='search-block'>"
                               + "<select class='search-term' multiple='true' "
                               + "size='" + size + "' name='" + name + "' id='" + name +"'>"
                               + "</select>" + select_all + "</div>";
                var searchlet = $(this).parents(".searchlet");
                $(this).after(select_all).parent().after(add_remove + selected);

                /* Handy handler for selecting everything on a select */
                $(".select-all-action", searchlet).click(function() {
                        $(this).prev("select").children("option").attr("selected", "selected");
                        return false;
                    });

                /* Aux function for the add and delete actions */
                function move_selected_options(src, dst) {
                    src.children("option:selected")
                        .clone().appendTo(dst)
                        .end().remove();
                }

                /* Move selected options from the left select to the right */
                $("button.add", searchlet).click(function () {
                        var parent_div = $(this).parent();
                        var src = parent_div.prev().children("select");
                        var dst = parent_div.next().children("select");
                        move_selected_options(src, dst);
                        dst.trigger("options-changed");
                        return false;
                    });

                /* Move selected options from the right select to the left */
                $("button.delete", searchlet).click(function () {
                        var parent_div = $(this).parent();
                        var src = parent_div.prev().children("select");
                        var dst = parent_div.next().children("select");
                        move_selected_options(dst, src);
                        dst.trigger("options-changed");
                        return false;
                    });

            }); // end of each
    }; // end of easySelect

    $.fn.smartsearch = function (options) {

        var settings = $.extend({}, $.fn.smartsearch.defaults, options);

        return this.each(function () {
                var container = this;
                var query = $(".query", container);
                var form = $("form", container);

                $("input, textarea, select, button", form).removeAttr("disabled");

                /* Hide the button until we have a query filter */
                $(".search-action").hide();

                /* Some things are hidden by default for accesibility reasons */
                $("#search-sections").show();

                $(".searchlet select", container).easySelect();

                /* Display the matching searchlet when clicking on a search section
                   e.g. simulate tabs */
                $(".search-section", container).click(function () {
                        /* show the matching searchlet */
                        $(".searchlet", container).hide();
                        var searchlet = $(this).attr("searchlet");

                        /* Disable the search term until an operator is chosen */
                        $("#" + searchlet + "-searchlet").show()
                            .children(".search-term").attr("disabled", "disabled");

                        /* highlight the selected section */
                        $("#search-sections li", container).removeClass("selected");
                        $(this).parent("li").addClass("selected"); 
                        return false;
                    });

                // Enable inputs (we disabled them in the submit of the form)
                $("input, textarea, select", form).removeAttr("disabled");

                /* When choosing an operator, hightlight it */
                $(".operators li input", container).click(function () {
                        $(this).parents(".operators").children().removeClass("selected");
                        $(this).parents("li").addClass("selected");
                        $(this).parents("div.searchlet").children(".search-term").removeAttr("disabled").val("").focus();
                        $("a", query).removeClass("editing");
                    });

                /* Function that connect some events to manipulate 
 		           a query arg */ 
                function setup_query_arg() { 
                    $(this).click(edit_query_arg) 
                        .next("button").click(remove_query_arg) 
                        .parent("span").hover(function(){$(this).addClass("show-button")}, 
                                              function(){$(this).removeClass("show-button")}); 
                }

 		        if ($("a", query).each(setup_query_arg).length > 0) { 
                    $(".search-action", container).show(); 
                } else { 
                    $(".search-action").hide(); 
                } 

                /* Function to allow edition on a query arg */
                function edit_query_arg() {
                    var attr = $(this).attr("href");
                    var query_type = $(this).attr("name");
                    // select the searchlet
                    $("button.search-section[searchlet='" + attr + "']", container).click();
                    // select the query type
                    if (query_type != "") {
                        $("#" + attr + "-searchlet input[value='" + query_type + "']", container).change().click();
                        // put the value in the input
                        $("#" + attr + "-searchlet .search-term").val($("span", this).html());
                    }
                    $("a", query).removeClass("editing");
                    $(this).addClass("editing");
                    return false;
                }

                function remove_query_arg() {
                    var query_arg = $(this).attr("name");
                    var attr = $(this).attr("attr");
                    $("#" + query_arg, query).parents("span.query-arg").remove();
                    $("#" + attr + "-searchlet input.search-term").val("");
                    $("#" + attr + "-searchlet textarea.search-term").val("");
                    $("#" + attr + "-searchlet input[type=radio]:checked").removeAttr("checked");
                    $("#" + attr + "-searchlet .operators li").removeClass("selected");
                    return false;
                }

                function update_query_args(attr, query_type, value, description) {
                    var n_args = $(".query span.query-arg", container).length;

                    var query_arg = attr + "-" + query_type + "-query-arg";

                    if ($("#" + query_arg, query).length == 0) {
                        if (value != "") {
                            var remove_button = '<button class="remove-action" name="'
                                + query_arg + '" attr="' + attr + '">'
                                + settings.remove_text + '</button>';
                            var contents = '<span class="query-arg">'
                                + (n_args == 0 ? description : settings.separator + ' ' + description)
                                + ' <a id="' + query_arg + '" name="' + query_type + '">'
                                + value
                                + '</a>' + remove_button + '</span>';
                            $(query).append(contents);
                    
                            // Set the href attribute the using jQuery function because
                            // otherwise Internet Explorer will prepend the full
                            // host + path to the href. For example: if you set
                            // <a href="' + attr + '"> Internet Explorer will do
                            // <a href="http://localhost:8000/foo/bar/attr">
                            $("#" + query_arg, query).attr("href", attr);

                            // Setup a click handler for the query_arg
                            // link to allow edition
                            $("#" + query_arg, query).each(setup_query_arg);

                            n_args += 1;
                        }
                    } else {
                        if (value != "") {
                            $("#" + query_arg, query).html(value);
                        } else {
                            $("#" + query_arg, query).parents("span.query-arg").remove();
                            n_args -= 1;
                        }
                    }

                    if (n_args == 0) {
                        $(".search-action", container).hide();
                    } else {
                        $(".search-action", container).show();
                    }

                }

                /* When typing on a search term update the query */
                $("input[type=text].search-term, textarea.search-term", container).keypress(function (event) {
                        var search_term = this;
                        var searchlet = $(this).parent(".searchlet");
                        var attr = $(this).attr("name");
                        var description = settings.description_map[attr];
                        //console.debug(event.keyCode);

                        keypress_delayed_handler = function () {
                            var operator_element = $("input[name='" + attr + ".operator']:checked", searchlet);
                            var operator_description = operator_element.next("label").html();

                            var operator = operator_element.val();

                            var value = $(search_term).val();
                            if (value != "") {
                                value = operator_description + " <span>" + value + "</span>";
                            }

                            update_query_args(attr, operator, value, description);

                        };

                        if (event.which != 13) { // Enter key
                            setTimeout(keypress_delayed_handler, settings.update_delay);
                        } else {
                            form.submit(); // TODO
                        }

                    });


                /* Query updater for select widgets */
                $("select.search-term", container).bind("options-changed", function () {
                        var search_term = this;
                        var attr = $(this).attr("name");
                        var description = settings.description_map[attr];
                        var values = $.map($(this).children("option"), function (n, i) {
                                return $(n).html();
                            });
                        var value = values.join(", ");
                        update_query_args(attr, "in", value, description);
                    });
        
                // Query updater for radio buttons
                $("input[type=radio].search-term", container).change(function () {
                        var search_term = this;
                        var parts = $(this).attr("name").split("__");
                        var attr = parts[0];
                        var operator = parts[1];
                        var description = settings.description_map[attr];
                        var value = '<span name="' + operator + '">'
                            + '<span class="' + $(this).val() + '">'
                            + $(this).next("label").html() + '</span></span>';
                        update_query_args(attr, operator, value, description);
                    });


                // Prepare the data for the GET request
                form.submit(function () {
                        // Disable all inputs so we don't send rubbish
                        $("input, textarea, select, button", form).attr("disabled", "disabled");

                        $("span.query-arg a", query).each(function () {
                                var attr = $(this).attr("href");
                                var query_type = $(this).attr("name");

                                var name = attr +  '__' + query_type;

                                if (query_type == "in") {
                                    // The value is the id of earch selected option
                                    var ids = $.map($("select#" + attr + " option", form),
                                                    function (option, i) {
                                                        return $(option).val();
                                                    });
                                    for(i=0; i<ids.length; i++){
                                        value = ids[i];
                                        var  hidden = "<input type='hidden' name='" + name + "' value='" + value + "'/>";
                                        form.append(hidden);
                                    }
                                } else if (query_type == "is") {
                                    var value = $("span", this).attr("name");
                                    var hidden = "<input type='hidden' name='" + name + "' value='" + value + "'/>";
                                    form.append(hidden);                    
                                } else {
                                    var outer_span = $("span", this);
                                    var inner_span = $("span span", this);
                                    var value = "";
                                    if (inner_span.length > 0) {
                                        value = inner_span.attr("class");
                                    } else {
                                        value = outer_span.html();
                                    }
                                    var hidden = "<input type='hidden' name='" + name + "' value='" + value + "'/>";
                                    form.append(hidden);
                                }
                            });
                    });

            }); // end of each
    }; // end of smartsearch

    $.fn.smartsearch.defaults = {
        update_delay: 500,
        separator: "and",
        remove_text: "remove",
        descriptions_map: {}
    };

})(jQuery);
 