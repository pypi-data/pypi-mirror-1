<div class="gibetagsdisplay" xmlns:py="http://purl.org/kid/ns#">
  <span class="tags_label" py:if="tags">
    Tags:
  </span>
  <span class="tags">
    <span py:for="i, tag in enumerate(tags)" py:strip="True"><span py:if="i != 0" py:strip="True">, </span><a href="${url_for('tags', tag=tag)}" rel="tag" class="tag" py:content="tag.display_name">me</a></span>
  </span>
</div>
