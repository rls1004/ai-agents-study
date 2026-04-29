PAGE_ASSET_GENERATOR_DESCRIPTION = """
Parallel asset generation agent for a 5-page Korean children's storybook.

Runs five image generator agents concurrently, one for each storybook page.
Each image generator reads story_writer_output from state and uses the page visual_description together with the global art_style and character descriptions to generate a consistent illustration.

Ensures all page images follow the same visual style, character design, and child-friendly storybook tone.
"""