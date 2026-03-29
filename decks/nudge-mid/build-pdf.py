"""Build PDF from slide HTML files + insert JPG image between slide 5 and 6."""
import asyncio
import os
from pathlib import Path

async def main():
    from playwright.async_api import async_playwright
    import fitz  # PyMuPDF

    deck_dir = Path(__file__).parent
    output_pdf = deck_dir / "NUDGE_중간발표.pdf"
    image_path = deck_dir / "PPT 추가자료.jpg"

    # Slide order: 1-5, then image, then 6-8
    slide_files = [
        "slide-01.html", "slide-02.html", "slide-03.html",
        "slide-04.html", "slide-05.html",
        # IMAGE INSERTED HERE
        "slide-06.html", "slide-07.html", "slide-08.html",
    ]

    # Width/Height for 16:9 at 1280x720
    width = 1280
    height = 720

    print("Launching browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height})

        pdf_pages = []  # list of PNG bytes

        for i, slide_file in enumerate(slide_files):
            slide_path = deck_dir / slide_file
            if not slide_path.exists():
                print(f"  SKIP: {slide_file} not found")
                continue

            url = f"file://{slide_path.resolve()}"
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(0.5)  # let fonts/css settle

            png_bytes = await page.screenshot(
                type="png",
                clip={"x": 0, "y": 0, "width": width, "height": height}
            )
            pdf_pages.append(("slide", png_bytes, slide_file))
            print(f"  Captured: {slide_file}")

            # After slide-05, insert image
            if slide_file == "slide-05.html" and image_path.exists():
                pdf_pages.append(("image", str(image_path), "PPT 추가자료.jpg"))
                print(f"  Inserted: PPT 추가자료.jpg (after slide-05)")

        await browser.close()

    # Build PDF with PyMuPDF
    print("\nBuilding PDF...")
    doc = fitz.open()

    for page_type, data, name in pdf_pages:
        if page_type == "slide":
            # PNG screenshot → PDF page
            img = fitz.open(stream=data, filetype="png")
            img_page = img[0]
            # Create page at 1280x720 points (16:9)
            pdf_page = doc.new_page(width=width, height=height)
            pdf_page.insert_image(
                fitz.Rect(0, 0, width, height),
                stream=data,
            )
            img.close()
        elif page_type == "image":
            # JPG image → fit to 1280x720 page with black background
            img = fitz.open(data)
            img_page = img[0]
            img_w, img_h = img_page.rect.width, img_page.rect.height

            pdf_page = doc.new_page(width=width, height=height)

            # Fill black background
            pdf_page.draw_rect(fitz.Rect(0, 0, width, height), color=(0, 0, 0), fill=(0.06, 0.09, 0.16))

            # Scale image to fit within page while maintaining aspect ratio
            scale_w = width / img_w
            scale_h = height / img_h
            scale = min(scale_w, scale_h)

            new_w = img_w * scale
            new_h = img_h * scale
            x_offset = (width - new_w) / 2
            y_offset = (height - new_h) / 2

            pdf_page.insert_image(
                fitz.Rect(x_offset, y_offset, x_offset + new_w, y_offset + new_h),
                filename=data,
            )
            img.close()

        print(f"  Added page {doc.page_count}: {name}")

    doc.save(str(output_pdf))
    doc.close()
    print(f"\n✅ PDF saved: {output_pdf}")
    print(f"   Total pages: {len(pdf_pages)}")

asyncio.run(main())
