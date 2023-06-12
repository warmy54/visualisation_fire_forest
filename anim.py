import vtk
from main import *


class vtkTimerCallback():
    def __init__(self, steps, interactor, dryFuelActor, fuelMappers, fireVolume, fireVolumeMappers, streamActor,
                 streamMappers):
        self.timer_count = 0
        self.steps = steps
        self.dryFuelActor = dryFuelActor
        self.interactor = interactor
        self.timerId = None
        self.fuelMappers = fuelMappers
        self.lock = False
        self.fireVolume = fireVolume
        self.fireVolumeMappers = fireVolumeMappers
        self.streamActor = streamActor
        self.streamMappers = streamMappers

    def execute(self, obj, event):
        if self.lock:
            return
        self.lock = True

        while self.timer_count < self.steps:
            print(self.timer_count)
            fuelMapper = self.fuelMappers[0]
            volumeMapper = self.fireVolumeMappers[0]
            streamMapper = self.streamMappers[0]

            self.fuelMappers.remove(self.fuelMappers[0])
            self.fireVolumeMappers.remove(self.fireVolumeMappers[0])
            self.streamMappers.remove(self.streamMappers[0])

            self.dryFuelActor.SetMapper(fuelMapper)
            self.fireVolume.SetMapper(volumeMapper)
            self.streamActor.SetMapper(streamMapper)
            self.interactor = obj
            self.interactor.GetRenderWindow().Render()
            self.interactor.ProcessEvents()
            self.timer_count += 1

        if self.timerId:
            self.interactor.DestroyTimer(self.timerId)


def main():
    renderer, renderWindow, renderWindowInteractor = getRendererRenderWindowAndInteractor(1920, 1080)

    fuelMappers = []
    volumeMappers = []
    streamMappers = []

    # Only animate relevant time steps to conserve ram usage
    for step in range(5, 16):
        print(step)

        reader = vtk.vtkXMLImageDataReader()
        if step < 10:
            name = "data/output.0" + str(step) + "000.vti"
        else:
            name = "data/output." + str(step) + "000.vti"
        reader.SetFileName(name)
        reader.Update()

        # create seedline
        seedline = vtk.vtkLineSource()
        seedline.SetResolution(100)
        seedline.SetPoint1(0.0, 300.0, 230.0)
        seedline.SetPoint2(0.0, -300.0, 230.0)

        streamMappers.append(getStreamLineMapper(reader, seedline))
        fuelMappers.append(getDryFuelMapper(reader))
        volumeMappers.append(getFireMapper(reader))

    fireVolume = vtk.vtkVolume()
    fireVolume.SetMapper(volumeMappers[0])
    fireVolume.SetProperty(getTransferFunctionProperty())

    fuelActor = vtk.vtkActor()
    fuelActor.SetMapper(fuelMappers[0])

    streamActor = vtk.vtkActor()
    streamActor.SetMapper(streamMappers[0])
    renderer.AddActor(streamActor)

    renderer.AddActor(fuelActor)
    renderer.AddVolume(fireVolume)

    camera = vtk.vtkCamera()
    camera.SetPosition(1000, 600, 500)
    camera.SetFocalPoint(0, 0, 0)
    camera.Roll(270)
    camera.SetThickness(2500)

    renderer.SetActiveCamera(camera)

    renderWindow.Render()

    # Initialize must be called prior to creating timer events.
    renderWindowInteractor.Initialize()

    # Sign up to receive TimerEvent
    cb = vtkTimerCallback(10, renderWindowInteractor, fuelActor, fuelMappers, fireVolume, volumeMappers, streamActor,
                          streamMappers)
    renderWindowInteractor.AddObserver('TimerEvent', cb.execute)
    cb.timerId = renderWindowInteractor.CreateRepeatingTimer(500)

    # start the interaction and timer
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == '__main__':
    main()
