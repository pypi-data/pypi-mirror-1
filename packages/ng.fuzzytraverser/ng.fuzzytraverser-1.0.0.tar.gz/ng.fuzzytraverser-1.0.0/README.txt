Short package description
=========================

Package developed to provide possibility display web pages correctly when
URL issued with a few misstakes (changing and missing letters, etc).

Package consist from three paths:

    FuzzyTraverser
        To turn on fuzzy traverser, interface IFuzzyTraverser must be
        appointed to container, traversed by this way. For example,
        see some ZCML-directive::
        
            <class class="zope.app.folder.folder.Folder">
                <implements 
                    interface="ng.fuzzytraverser.interfaces.IFuzzyTraverser"
                />
            </class>

        All content names of this container may be miss entered into url-bar
        of your browser. Error sensibility of fuzzy traverser can be
        customize by means of special utility or annotations of traversed
        containers;
        
    FuzzyTraverserProperties
        The IFuzzyTraverserProperties utility can be added into local
        site-manager and get enable possibility set fuzzy traverse
        parameters. The utility must be registered with interface printed
        bellow::
        
            ng.fuzzytraverser.fuzzytraverserproperties.interfaces.IFuzzyTraverserProperties 
            
        Custom parameters followed:
        
            On
                Fuzzy traverser turn on (it worked as ordinal traverser otherwize);
                
            Rate
                Detectiob threshold - this is maximal corruption grade on
                which name can be determined yet. Entering values above 0.5
                is not recomended;
                
            Use
                The parameter reserved on future.

    FuzzyTraverserAnnotation
        To turn on customize traverser in defferent areas of site tree, you
        can customize via annotations of traversed containers. Interface
        IFuzzyTraverserAnnotable must be appointed on container to get such
        posibiblity. For example::
        
            <class class="zope.app.folder.folder.Folder">
                <implements 
                    interface="ng.fuzzytraverser.fuzzytraverserannotation.\
                        interfaces.IFuzzyTraverserAnnotable"
                    /> 
            </class>

        After what each object provided such interface
        (zope.app.folder.folder.Folder in our sample) be have page titled
        FuzzyTraverser. Parameters to custom on this page are followed:

            On 
                Fuzzy traverser turn on (it worked as ordinal traverser
                otherwize);
                
            Rate 
                Detectiob threshold - this is maximal corruption grade on
                which name can be determined yet. Entering values above 0.5
                is not recomended;
                
            Use
                This annotation parameters will be used to get solution.
                
Short recomends for use
-----------------------

Product highly resourse hungry and it turn on for containers large then 100
items is not recommends.

