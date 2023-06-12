from pickle import FALSE
import random
import time
import vtk
from steam import renderStreamMapper
from steam import renderStreamMapper
class vtkTimerCallback():
    def __init__(self, steps, iren, actor, fuelmappers,volume, volumemappers,streamActor, streamMappers,names):
        self.timer_count = 0
        self.steps = steps
        self.actor = actor
        self.iren = iren
        self.timerId = None
        self.fuelmappers = fuelmappers
        self.lock = False
        self.volume = volume
        self.volumemappers = volumemappers
        self.streamActor = streamActor
        self.streamMappers = streamMappers
        self.names = names
        

    def execute(self, obj, event):
       
        if self.lock:
            return
        self.lock = True
        while self.timer_count < self.steps :
            print(self.timer_count)
            fuelmapper = self.fuelmappers[0]
            volumemapper = self.volumemappers[0]
            streamMapper = renderStreamMapper(self.names[self.timer_count])
            
            self.fuelmappers.remove(self.fuelmappers[0])
            self.volumemappers.remove(self.volumemappers[0])
            
            
            self.actor.SetMapper(fuelmapper)
            self.volume.SetMapper(volumemapper)
            self.streamActor.SetMapper(streamMapper)
            self.iren = obj
            self.iren.GetRenderWindow().Render()
            self.iren.ProcessEvents()
            self.timer_count += 1
            #time.sleep(1)
        if self.timerId :
            self.iren.DestroyTimer(self.timerId)




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
    names = []
    fuelMappers = []
    volumeMappers = []
    streamMappers = []
    stream = False
    for step in range(5,16):
        print(step)

        reader = vtk.vtkXMLImageDataReader()
        if step < 10:
            name = "visualisation_fire_forest/data/output.0"+str(step)+"000.vti"
        else:
            name = "visualisation_fire_forest/data/output."+str(step)+"000.vti"
        reader.SetFileName(name)
        names.append(name)
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



        fuelMapper = vtk.vtkPolyDataMapper()
        fuelMapper.SetInputConnection(glyph3D.GetOutputPort())
        fuelMappers.append(fuelMapper)
        
        reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('theta'))

        # raycast mapper
        rayCastMapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
        rayCastMapper.SetInputConnection(reader.GetOutputPort())
        volumeMappers.append(rayCastMapper)
        
        if stream == False: 
            streamMappers.append(renderStreamMapper(name))
            stream = True
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
    volume.SetMapper(volumeMappers[0])
    volume.SetProperty(volumeProperty)
        

    fuelActor = vtk.vtkActor()
    fuelActor.SetMapper(fuelMappers[0])

    streamActor = vtk.vtkActor()
    streamActor.SetMapper(streamMappers[0])
    
    renderer.AddActor(fuelActor)
    renderer.AddVolume(volume)
    renderer.AddActor(streamActor)
    


    camera = vtk.vtkCamera()
    camera.SetPosition(1000,600,500)
    camera.SetFocalPoint(0,0,0)
    camera.Roll(270)
    camera.SetThickness(2500);
    
    renderer.SetActiveCamera(camera)

    renderWindow.Render()

    # Initialize must be called prior to creating timer events.
    renderWindowInteractor.Initialize()

    # Sign up to receive TimerEvent
    cb = vtkTimerCallback(10, renderWindowInteractor, fuelActor, fuelMappers, volume, volumeMappers,streamActor, streamMappers,names)
    renderWindowInteractor.AddObserver('TimerEvent', cb.execute)
    cb.timerId = renderWindowInteractor.CreateRepeatingTimer(500)

    # start the interaction and timer
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == '__main__':
    main()