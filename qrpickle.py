from subprocess import check_call
from os.path import join
from tempfile import mkdtemp
from multiprocessing.pool import ThreadPool

import numpy as np
from PIL import Image
import zbar
from pyPdf import PdfFileWriter, PdfFileReader
import qrcode


def array_to_reprs(a, step=20):
    yield 'zeros(%s)' % str(a.shape)
    a = a.flatten()
    for i in range(0, len(a), step):
        yield repr(a[i:i+step])


def reprs_to_pngs(reprs, prefix='.'):
    for i,r in enumerate(reprs):
        img = qrcode.make(r)
        name = join(prefix, 'img%i.pdf' % i)
        img.save(name)
        yield name


def convert(in_name, out_name, nprocs=4):
    pool = ThreadPool(processes=nprocs)
    args = (['convert', i, o] for i, o in zip(in_name, out_name))
    pool.imap_unordered(check_call, args)


def convert2(names, name_func, nprocs=4):
    pool = ThreadPool(processes=nprocs)
    def converter(in_name):
        out_name = name_func(in_name)
        check_call(['convert', in_name, out_name])
        return out_name

    return pool.imap_unordered(converter, names)


def png2pdf(in_name):
    out_name = in_name[:-3] + 'pdf'
    check_call(['convert', in_name, out_name])
    return out_name


def pngs_to_reprs(pngs):
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')

    for path in pngs:
        im = Image.open(path).convert('L')
        w, h = im.size
        raw = im.tostring()
        im2 = zbar.Image(w, h, 'Y800', raw)
        scanner.scan(im2)
        for s in im2:
            yield s.data


def merge_pdfs(name, pdfs):
    merged = PdfFileWriter()
    files = (file(p, 'rb') for p in pdfs)
    for f in files:
        merged.addPage(PdfFileReader(f).getPage(0))
    with file(name, 'wb') as os:
        merged.write(os)
    [f.close() for f in files]


def split_pdf(path, pattern, prefix='.'):
    big_pdf = PdfFileReader(file(path, 'rb'))
    for page_num in range(big_pdf.getNumPages()):
        single_page_pdf = PdfFileWriter()
        single_page_pdf.addPage(big_pdf.getPage(page_num))

        out_name = join(prefix, pattern % page_num)
        with file(out_name, 'wb') as out_stream:
            single_page_pdf.write(out_stream)
        yield out_name


def reprs_to_array(reprs, step=20):
    from numpy import zeros
    from numpy import array
    reprs = [r for r in reprs]
    b = eval(reprs[0])
    shape = b.shape
    c = b.flatten()
    slice_reprs = reprs[1:]
    for i,r in zip(range(0, len(c), step), slice_reprs):
        c[i:i+step] = eval(r)
    b = c.reshape(shape)
    return b


def dump(a, path, work_dir=None):
    if work_dir is None:
        work_dir = mkdtemp()
    reprs = array_to_reprs(a)
    pngs_orig = reprs_to_pngs(reprs, prefix=work_dir)
    pdfs = convert2(pngs_orig, lambda x: x[:-3]+'pdf')
    merge_pdfs(path, pdfs)


def load(path, work_dir=None):
    if work_dir is None:
        work_dir = mkdtemp()
    pdfs = split_pdf(path, 'page%i.pdf', prefix=work_dir)
    pngs = convert2(pdfs, lambda x: x[:-3]+'png')
    reprs = pngs_to_reprs(pngs)
    return reprs_to_array(reprs)


a = np.linspace(0, 10, 20)
dump(a, 'merged.pdf')
a2 = load('merged.pdf')
print a
print a2
