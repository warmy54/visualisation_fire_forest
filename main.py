from re import M
import vtk
from steam import renderStreamMapper
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
    name = "visualisation_fire_forest/data/output.14000.vti"
    reader.SetFileName(name)
    reader.Update()
    #print(reader.GetOutput().GetPointData())
    reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('rhof_1'))
    reader.Update()
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

    # ----------------------------------------------------------------
    # Wind Streamlines
    # ----------------------------------------------------------------

    mapper = renderStreamMapper(name)

    streamLineActor = vtk.vtkActor()
    streamLineActor.SetMapper(mapper)
    streamLineActor.VisibilityOn();

    
    # ----------------------------------------------------------------
    # Circle for debuging
    # ----------------------------------------------------------------
    colors = vtk.vtkNamedColors()
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetCenter(300.0, 300.0, 300.0)
    sphereSource.SetRadius(30.0);
    # Make the surface smooth.
    sphereSource.SetPhiResolution(100)
    sphereSource.SetThetaResolution(100)

    newmapper = vtk.vtkPolyDataMapper()
    newmapper.SetInputConnection(sphereSource.GetOutputPort())

    sphereactor = vtk.vtkActor()
    sphereactor.SetMapper(newmapper)
    #sphereactor.GetProperty().SetColor(colors.GetColor3d("Cornsilk").GetData())

    camera = vtk.vtkCamera()
    camera.SetPosition(1700,0,1500)
    camera.SetFocalPoint(50,0,100)
    camera.Roll(270)
    camera.SetThickness(2500);
    renderer.SetActiveCamera(camera)


    # add actor and renders
    renderer.AddActor(actor)
    renderer.AddVolume(volume)
    #renderWindow.AddRenderer(whiteRender)
    renderer.AddActor(streamLineActor)
    #renderer.AddActor(sphereactor)
    
    # enter the rendering loop
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == "__main__":
    main()