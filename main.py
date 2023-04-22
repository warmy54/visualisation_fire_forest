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

    # ----------------------------------------------------------------
    # read the data set
    # ----------------------------------------------------------------
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("data/output.15000.vti")
    reader.Update()

    arraySelection = reader.GetPointDataArraySelection()
    arraySelection.DisableAllArrays()
    arraySelection.EnableArray('theta')
    reader.Update()

    data = reader.GetOutput()
    data.GetPointData().SetScalars(data.GetPointData().GetArray(0))

    # ----------------------------------------------------------------
    # marching cubes
    # ----------------------------------------------------------------
    # extract the surface with vtkMarchingCubes
    isosurface = vtk.vtkMarchingCubes()
    isosurface.SetInputData(data)
    isosurface.SetValue(0, 300)

    # apply a vtkPolyDataMapper to the output of marching cubes
    dataMapper = vtk.vtkPolyDataMapper()
    dataMapper.SetInputConnection(isosurface.GetOutputPort(0))
    dataMapper.ScalarVisibilityOff()

    # create a vtkActor and assign the mapper
    actor = vtk.vtkActor()
    actor.SetMapper(dataMapper)

    # get renderer for the white background and interactor style
    whiteRender = vtk.vtkRenderer()
    whiteRender.SetViewport([1, 0, 1, 1])
    whiteRender.SetBackground([1, 1, 1])

    # get mouse style for interactor
    styleTrackball = vtk.vtkInteractorStyle3D()


    # ----------------------------------------------------------------
    # DirectVolume
    # ----------------------------------------------------------------

    # raycast mapper
    rayCastMapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
    rayCastMapper.SetInputData(data)

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
    # renderer.AddActor(actor) # UNCOMMENT THIS LINE TO GET THE MARCHING CUBE IMAGE
    renderer.AddVolume(volume)
    renderWindow.AddRenderer(whiteRender)

    # enter the rendering loop
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == "__main__":
    main()