<div xmlns:py="http://purl.org/kid/ns#">
    <table id="${name}" class="grid paginated_ajax_grid" cellspacing="1">
        <thead py:if="columns">
            <tr>
                <th colspan="${len(columns)}" class="navigator">
                    <div id="${name}_nav_links" class="nav_links"></div>
                    <div class="spinner">
                        <img id="${name}_spinner" alt="spinner" style="display: none;"
                             src="/tg_widgets/tgpaginate.images/spinner.gif" />
                    </div>
                    <div id="${name}_page_info" class="page_info"></div>
                </th>
            </tr>
            <tr>
                <th py:for="i, col in enumerate(columns)" class="col_${i}">
                    <a py:if="col.get_option('sortable', False) and getattr(tg, 'paginate', False)" 
                       href="${tg.paginate[value.var_name].get_href(1, col.name, col.get_option('reverse_order', False))}">${col.title}</a>
                    <span py:if="not getattr(tg, 'paginate', False) or not col.get_option('sortable', False)" py:replace="col.title"/>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td></td>
            </tr>
        </tbody>
    </table>
    <script type="text/javascript">
        new PaginatedAjaxGrid('${name}', ${options});
    </script>
</div>