from pynetcdf import NetCDFFile

def save(dataset, filename):
    out = NetCDFFile(filename, 'w')

    for var in dataset.walk():
        print var


if __name__ == '__main__':
    from dap.client import open

    dataset = open('http://test.pydap.org/coads.nc', verbose=1)
    save(dataset, 'test.nc')
