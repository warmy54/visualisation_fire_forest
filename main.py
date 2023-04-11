import vtk
import numpy as np



# ----------------------------------------------------------------
# create image button
# ----------------------------------------------------------------
def CreateImage(image: vtk.vtkImageData, color1: list, color2: list):
    # Specify the size of the image data
    image.SetDimensions(10, 10, 1)
    image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 3)
    dims = image.GetDimensions()

    # Fill the image with
    for y in range(dims[1]):
        for x in range(dims[0]):
            color = color1 if x < 5 else color2
            for c in range(3):
                image.SetScalarComponentFromDouble(x, y, 0, c, color[c])


# Callback for the slider interaction
class vtkSliderCallback(object):
    def __init__(self, MarchingCubes):
        self.MarchingCubes = MarchingCubes

    def __call__(self, sliderWidget, eventId):
        self.MarchingCubes.SetValue(0, sliderWidget.GetRepresentation().GetValue())


def main():
    # ----------------------------------------------------------------
    # create the renderer and window interactor
    # ----------------------------------------------------------------
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(768, 400)

    renderer = vtk.vtkRenderer()
    renderer.SetViewport(0, 0, 0.66666, 1.0)
    renderer.SetBackground(1, 1, 1)
    renderWindow.AddRenderer(renderer)

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # ----------------------------------------------------------------
    # create image button to change screens
    # ----------------------------------------------------------------
    # Create two images for texture
    green = [145, 207, 96]
    gray = [153, 153, 153]
    image1 = vtk.vtkImageData()
    image2 = vtk.vtkImageData()
    CreateImage(image1, green, gray)
    CreateImage(image2, gray, green)

    # Create the widget and its representation
    buttonRepresentation = vtk.vtkTexturedButtonRepresentation2D()
    buttonRepresentation.SetNumberOfStates(2)
    buttonRepresentation.SetButtonTexture(0, image1)
    buttonRepresentation.SetButtonTexture(1, image2)

    buttonWidget = vtk.vtkButtonWidget()
    buttonWidget.SetInteractor(renderWindowInteractor)
    buttonWidget.SetRepresentation(buttonRepresentation)

    # Place the widget. Must be done after a render so that the viewport is defined.
    # Here the widget placement is in normalized display coordinates
    upperLeft = vtk.vtkCoordinate()
    upperLeft.SetCoordinateSystemToNormalizedDisplay()
    upperLeft.SetValue(0, 1.0)

    bds = [0] * 6
    sz = 50.0
    bds[0] = upperLeft.GetComputedDisplayValue(renderer)[0] - sz
    bds[1] = bds[0] + sz
    bds[2] = upperLeft.GetComputedDisplayValue(renderer)[1] - sz
    bds[3] = bds[2] + sz
    bds[4] = bds[5] = 0.0

    # Scale to 1, default is .5
    buttonRepresentation.SetPlaceFactor(1)
    buttonRepresentation.PlaceWidget(bds)
    buttonWidget.On()

    # ----------------------------------------------------------------
    # read the volume data set
    # ----------------------------------------------------------------
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("data/output.01000.vti")
    reader.Update()

    data = reader.GetOutput()

    arrayFilter = vtk.vtkPassArrays()
    arrayFilter.SetInputData(data)
    arrayFilter.AddPointDataArray("rhof_1")
    print(arrayFilter.GetOutput())

    # extract the surface with vtkMarchingCubes
    isosurface = vtk.vtkMarchingCubes()
    isosurface.SetInputConnection(arrayFilter.GetOutputPort(0))
    isosurface.SetValue(0, 300)


    # apply a vtkPolyDataMapper to the output of marching cubes
    dataMapper = vtk.vtkPolyDataMapper()
    dataMapper.SetInputConnection(isosurface.GetOutputPort(0))
    dataMapper.ScalarVisibilityOff()

    # create a vtkActor and assign the mapper
    actor = vtk.vtkActor()
    actor.SetMapper(dataMapper)

    # create a 2D slider
    sliderRep = vtk.vtkSliderRepresentation2D()
    sliderRep.SetMinimumValue(0)
    sliderRep.SetMaximumValue(600)
    sliderRep.SetValue(300)
    sliderRep.SetTitleText("Isovalue")
    # set color properties
    sliderRep.GetSliderProperty().SetColor(
        0.2, 0.2, 0.6
    )  # Change the color of the knob that slides
    sliderRep.GetTitleProperty().SetColor(
        0, 0, 0
    )  # Change the color of the text indicating what the slider controls
    sliderRep.GetLabelProperty().SetColor(
        0, 0, 0.4
    )  # Change the color of the text displaying the value
    sliderRep.GetSelectedProperty().SetColor(
        0.4, 0.8, 0.4
    )  # Change the color of the knob when the mouse is held on it
    sliderRep.GetTubeProperty().SetColor(0.7, 0.7, 0.7)  # Change the color of the bar
    sliderRep.GetCapProperty().SetColor(
        0.7, 0.7, 0.7
    )  # Change the color of the ends of the bar
    # set position of the slider
    sliderRep.GetPoint1Coordinate().SetCoordinateSystemToDisplay()
    sliderRep.GetPoint1Coordinate().SetValue(40, 40)
    sliderRep.GetPoint2Coordinate().SetCoordinateSystemToDisplay()
    sliderRep.GetPoint2Coordinate().SetValue(100, 40)
    sliderWidget = vtk.vtkSliderWidget()
    sliderWidget.SetInteractor(renderWindowInteractor)
    sliderWidget.SetRepresentation(sliderRep)
    sliderWidget.SetAnimationModeToAnimate()

    # create the callback
    callback = vtkSliderCallback(isosurface)
    sliderWidget.AddObserver("InteractionEvent", callback)

    # get renderer for the white background and interactor style
    whiteRender = vtk.vtkRenderer()
    whiteRender.SetViewport([0.66666, 0, 1, 1])
    whiteRender.SetBackground([1, 1, 1])

    # get mouse style for interactor
    styleTrackball = vtk.vtkInteractorStyleTrackballCamera()

    # isosurfaqce slider
    sliderWidget.EnabledOn()

    # add actor and renders
    renderer.AddActor(actor)
    renderWindow.AddRenderer(whiteRender)

    # enter the rendering loop
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == "__main__":
    main()