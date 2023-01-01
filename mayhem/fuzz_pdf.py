#!/usr/bin/env python3

import atheris
import sys
import fuzz_helpers

with atheris.instrument_imports(include=['pyhanko']):
    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

from pyhanko.pdf_utils.misc import PdfError
def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        with fdp.ConsumeMemoryFile(all_data=True, as_bytes=True) as f:
            if fdp.ConsumeBool():
                PdfFileReader(f)
            else:
                IncrementalPdfFileWriter(f)
    except PdfError:
        return -1

def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
