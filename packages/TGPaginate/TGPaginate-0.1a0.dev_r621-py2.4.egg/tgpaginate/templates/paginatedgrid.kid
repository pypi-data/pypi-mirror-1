<div xmlns:py="http://purl.org/kid/ns#">
    <table id="${name}" class="grid paginated_ajax_grid" cellspacing="1">
        <thead py:if="columns">
            <tr>
                <th colspan="${len(columns)}" class="navigator">
                    <div id="${name}_nav_links" class="nav_links">
                        <span py:if="not tg.paginate[var_name].current_page == 1">
                            <a href="${tg.paginate[var_name].get_href(1)}">&lt;&lt;</a>
                            <a href="${tg.paginate[var_name].get_href(tg.paginate[var_name].current_page-1)}">&lt;</a>
                        </span>
                        <span py:if="tg.paginate[var_name].page_count > 1" py:for="page in tg.paginate[var_name].pages">
                            <span py:if="page == tg.paginate[var_name].current_page" class="current_page">
                                [${page}]
                            </span>
                            <span py:if="page != tg.paginate[var_name].current_page">
                                <a href="${tg.paginate[var_name].get_href(page)}">${page}</a>
                            </span>
                        </span>
                        <span py:if="tg.paginate[var_name].pages and not tg.paginate[var_name].current_page == tg.paginate[var_name].page_count">
                            <a href="${tg.paginate[var_name].get_href(tg.paginate[var_name].current_page+1)}">&gt;</a>
                            <a href="${tg.paginate[var_name].get_href(tg.paginate[var_name].page_count)}">&gt;&gt;</a>
                        </span>
                    </div>
                </th>
            </tr>
            <tr>
                <th py:for="i, col in enumerate(columns)" class="col_${i}">
                    <a py:if="col.get_option('sortable', False) and getattr(tg, 'paginate', False)" 
                       href="${tg.paginate[var_name].get_href(1, col.name, col.get_option('reverse_order', False))}">${col.title}</a>
                    <span py:if="not getattr(tg, 'paginate', False) or not col.get_option('sortable', False)" py:replace="col.title"/>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr py:for="i, row in enumerate(value)" class="${i%2 and 'odd' or 'even'}">
              <td py:for="col in columns">
                ${col.get_field(row)}
              </td>
            </tr>
        </tbody>
    </table>        
</div>