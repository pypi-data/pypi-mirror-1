
def initialize(context):
    # Apply monkey patches

    from collective.discussionplus import patches
    patches.apply_patches()