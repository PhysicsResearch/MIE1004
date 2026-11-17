// Serves the starting code of Chapter 3 as a download, straight from examples/dicom_metadata.py,
// so the website always offers the same file as the repository.
import code from '@examples/dicom_metadata.py?raw';

export function GET() {
	return new Response(code, {
		headers: { 'Content-Type': 'text/x-python; charset=utf-8' },
	});
}
