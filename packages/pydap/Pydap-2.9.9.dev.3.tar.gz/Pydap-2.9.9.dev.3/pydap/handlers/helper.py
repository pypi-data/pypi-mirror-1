import copy

from pydap.model import *
from pydap.lib import isiterable, walk, parse_qs, fix_shn


def constrain(dataset, ce):
    projection, selection = parse_qs(ce)
    projection = projection or [[(key, ())]
            for key in dataset.keys()]

    # Start with an empty dataset.
    new_ = DatasetType(name=dataset.name,
            attributes=dataset.attributes.copy())

    for var in fix_shn(projection, dataset):
        target, template = new_, dataset
        while var:
            token, slice_ = var.pop(0)
            if token not in template:
                break
                        
            # We need to work on a copy of the template,
            # since occasionally we'll have to slice it.
            copy_ = copy.deepcopy(template[token])

            # If this is a partial request (not last) for a Grid,
            # return a Structure.
            if isinstance(copy_, GridType) and var:
                candidate = StructureType(
                        name=copy_.name,
                        attributes=copy_.attributes.copy())
            # Otherwise, return a copy of the var.
            else:
                candidate = copy.deepcopy(copy_)

            # Filter var and the copy_.
            if isinstance(candidate, SequenceType):
                filter_seq(candidate, selection)
                filter_seq(copy_, selection)

            # And slice them.
            if slice_:
                slice_var(candidate, slice_)
                slice_var(copy_, slice_)
            
            if isinstance(candidate, StructureType):
                # If this is a partial request for a Structure,
                # empty it to include only requested vars.
                if var:
                    candidate.clear()

                # Add the variable if it's not in the target,
                # or if it is the last token (ie, a complete
                # structure).
                if token not in target or not var:
                    target[token] = candidate
                target, template = target[token], copy_
            else:
                target[token] = candidate

    return new_


def slice_var(var, slice_):
    if isinstance(var, SequenceType): slice_ = slice_[0]
    var.data = var[slice_]
    try:
        var.shape = getattr(var.data, 'shape') 
    except (TypeError, AttributeError):
        pass

    if isinstance(var, GridType):
        if not isiterable(slice_):
            slice_ = (slice_,)
        for map_, mapslice in zip(var.maps.values(), slice_):
            map_.data = map_.data[mapslice]
            map_.shape = map_.data.shape
