"""Utility functions for manipulating portal_skins. portal_skins' native API is cumbersome for some common tasks; these wrappers make them easy."""


def deleteLayers(skinsTool, layersToDelete):
    """Remove each of the layers in `layersToDelete` from all skins.
    
    (We check them all, in case the user manually inserted it into some.)
    
    Pass getToolByName(portal, 'portal_skins') for `skinsTool`.
    
    """
    # Thanks to SteveM of PloneFormGen for a good example.
    for skinName in skinsTool.getSkinSelections():
        layers = [x.strip() for x in skinsTool.getSkinPath(skinName).split(',')]
        try:
            for curLayer in layersToDelete:
                layers.remove(curLayer)
        except ValueError:  # thrown if a layer ain't in there
            pass
        skinsTool.addSkinSelection(skinName, ','.join(layers))  # more like "set" than "add"