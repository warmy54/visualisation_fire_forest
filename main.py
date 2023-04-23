import vtk


def main():
    # ----------------------------------------------------------------
    # create the renderer and window interactor
    # ----------------------------------------------------------------
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(1200, 800)

    renderer = vtk.vtkRenderer()
    renderer.SetViewport(0, 0, 1.0, 1.0)
    renderer.SetBackground(1, 1, 1)
    renderWindow.AddRenderer(renderer)

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # get renderer for the white background and interactor style
    whiteRender = vtk.vtkRenderer()
    whiteRender.SetViewport([1, 0, 1, 1])
    whiteRender.SetBackground([1, 1, 1])

    # ----------------------------------------------------------------
    # read the data set
    # ----------------------------------------------------------------
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("data/output.14000.vti")
    reader.Update()

    reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('rhof_1'))

    # ----------------------------------------------------------------
    # Bulk Density of Dry Fuel
    # ----------------------------------------------------------------

    # Create a threshold filter to select points with values above a threshold
    threshold = vtk.vtkThresholdPoints()
    threshold.SetInputConnection(reader.GetOutputPort())
    threshold.ThresholdByUpper(0.2)
    threshold.Update()

    cylinderSource = vtk.vtkCylinderSource()
    cylinderSource.SetHeight(0.5)
    cylinderSource.SetRadius(0.1)
    cylinderSource.Update()

    transform = vtk.vtkTransform()
    transform.RotateX(90)
    transform.Update()

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(cylinderSource.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    glyph3D = vtk.vtkGlyph3D()
    glyph3D.SetInputConnection(threshold.GetOutputPort())
    glyph3D.SetSourceConnection(transformFilter.GetOutputPort())
    glyph3D.SetScaleModeToScaleByScalar()  # Map values to size of spheres
    glyph3D.SetScaleFactor(50)  # Set a default scaling factor
    glyph3D.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # ----------------------------------------------------------------
    # DirectVolume of Fire
    # ----------------------------------------------------------------

    reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('theta'))

    # raycast mapper
    rayCastMapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
    rayCastMapper.SetInputConnection(reader.GetOutputPort())
    # rayCastMapper.SetInputData(data)

    min_value = 310
    max_value = 900

    # transfer functions
    colorTransferFx = vtk.vtkColorTransferFunction()
    colorTransferFx.AddRGBPoint(min_value, 0.0, 0.0, 0.0)
    colorTransferFx.AddRGBPoint(315, 0.5, 0.5, 0.5)
    colorTransferFx.AddRGBPoint(390, 0.5, 0.5, 0.5)
    colorTransferFx.AddRGBPoint(400, 1, 0.5, 0.5)
    colorTransferFx.AddRGBPoint(max_value, 1.0, 0.0, 0.0)
    opacityTransferFx = vtk.vtkPiecewiseFunction()
    opacityTransferFx.AddPoint(min_value, 0.0)
    opacityTransferFx.AddPoint(315, 0.1)
    opacityTransferFx.AddPoint(390, 0.1)
    opacityTransferFx.AddPoint(450, 0.6)
    opacityTransferFx.AddPoint(max_value, 1.0)

    # assign transfer function to volume properties
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorTransferFx)
    volumeProperty.SetScalarOpacity(opacityTransferFx)
    volumeProperty.ShadeOff()
    volumeProperty.SetInterpolationTypeToLinear()

    # create volume actor and assign mapper and properties
    volume = vtk.vtkVolume()
    volume.SetMapper(rayCastMapper)
    volume.SetProperty(volumeProperty)

    # add actor and renders
    renderer.AddActor(actor)
    renderer.AddVolume(volume)
    renderWindow.AddRenderer(whiteRender)

    # enter the rendering loop
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == "__main__":
    main()