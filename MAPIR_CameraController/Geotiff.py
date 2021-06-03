# from osgeo import gdal
# # gdal.UseExceptions()
# # import gdal

# class Geotiff:

#     @staticmethod
#     def get_geo_data(in_geotiff_path):
#         in_geotiff = gdal.Open(in_geotiff_path)
#         projection = in_geotiff.GetProjection()
#         geo_transform = in_geotiff.GetGeoTransform()
#         gcps = in_geotiff.GetGCPs()
#         gcp_projection = in_geotiff.GetGCPProjection()
#         in_geotiff = None
#         return projection, geo_transform, gcps, gcp_projection

#     @staticmethod
#     def set_geo_data(geotiff, projection, geo_transform, gcps, gcp_projection):
#         geotiff.SetGeoTransform(geo_transform)
#         geotiff.SetProjection(projection)
#         geotiff.SetGCPs(gcps, gcp_projection)

#     @staticmethod
#     def write_bands_to_geotiff(geotiff, bands, nodata):
#         for i in range(len(bands)):
#             geotiff.GetRasterBand(i+1).WriteArray(bands[i])
#             geotiff.GetRasterBand(i+1).SetNoDataValue(nodata)

#     @staticmethod
#     def get_bands_from_image_data(image_data):
#         return [
#             image_data[:, :, 2],
#             image_data[:, :, 1],
#             image_data[:, :, 0],
#             image_data[:, :, 3],
#         ]

#     @staticmethod
#     def create_geotiff(image_data, out_geotiff_path):
#         bands = Geotiff.get_bands_from_image_data(image_data)
#         [cols, rows] = bands[0].shape
#         num_bands = 4

#         # if image_data.dtype == 'uint8':
#         #     gdal_dtype = gdal.GDT_UInt8
#         # elif image_data.dtype == 'uint16':
#         #     gdal_dtype = gdal.GDT_UInt16
#         gdal_dtype = gdal.GDT_UInt16

#         driver = gdal.GetDriverByName("GTiff")
#         out_geotiff = driver.Create(
#             out_geotiff_path,
#             rows,
#             cols,
#             num_bands,
#             gdal_dtype,
#             ['COMPRESS=LZW', 'PHOTOMETRIC=RGB', 'ALPHA=YES']
#         )
#         return out_geotiff

#     # @staticmethod
#     # def from_rgba(in_geotiff_path, image_data, out_geotiff_path):
#     #     out_geotiff = Geotiff.create_geotiff(image_data, out_geotiff_path)

#     #     projection, geo_transform, gcps, gcp_projection = Geotiff.get_geo_data(in_geotiff_path)

#     #     Geotiff.set_geo_data(out_geotiff, projection, geo_transform, gcps, gcp_projection)

#     #     bands = Geotiff.get_bands_from_image_data(image_data)
#     #     nodata = -10000
#     #     Geotiff.write_bands_to_geotiff(out_geotiff, bands, nodata)

#     #     out_geotiff.FlushCache()
#     #     out_geotiff = None
