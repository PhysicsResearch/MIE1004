// Serves the example code of Chapter 4 as a download, straight from examples/view_ct_series.py.
import code from '@examples/view_ct_series.py?raw';

export function GET() {
	return new Response(code, {
		headers: { 'Content-Type': 'text/x-python; charset=utf-8' },
	});
}
