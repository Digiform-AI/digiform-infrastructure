from pypdf import PdfWriter, PdfReader

path = "sample2page.pdf"

writer = PdfWriter()
reader = PdfReader(path)
writer.append_pages_from_reader(reader)
writer.remove_images()

with open(path, "wb") as output_stream:
    writer.write(output_stream)
output_stream.close()