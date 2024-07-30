import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import landing_page


class LandingPageTestCase(TestCase):
    def setUp(self):
        # Create test image files
        self.image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        self.landing_page_instance = landing_page.objects.create(
            header_section_one="Header 1",
            text_section_one="Text 1",
            image_section_one=self.image,
            header_section_two="Header 2",
            text_section_two="Text 2",
            image_section_two_left=self.image,
            image_section_two_header_left="Header 2 Left",
            image_section_two_text_left="Text 2 Left",
            image_section_two_right=self.image,
            image_section_two_header_right="Header 2 Right",
            image_section_two_text_right="Text 2 Right",
            header_section_three="Header 3",
            text_section_three="Text 3",
            image_section_three_left=self.image,
            image_section_three_right=self.image
        )

    def test_images_deleted_on_object_delete(self):
        # Ensure the files exist
        image_paths = [
            self.landing_page_instance.image_section_one.path,
            self.landing_page_instance.image_section_two_left.path,
            self.landing_page_instance.image_section_two_right.path,
            self.landing_page_instance.image_section_three_left.path,
            self.landing_page_instance.image_section_three_right.path,
        ]

        for image_path in image_paths:
            self.assertTrue(os.path.isfile(image_path))

        # Delete the object
        self.landing_page_instance.delete()

        # Ensure the files are deleted
        for image_path in image_paths:
            self.assertFalse(os.path.isfile(image_path))
