$Id: README.txt 35334 2008-01-25 14:33:40Z cray $

Дополнительная информация по директиве factoryform:

    Директива наследуется от директивы install и, соответственно, содержит
    поддирективы property. Выглядит она следующим образом::
        
        <factoryform
            name="demo"
            root="zope.app.folder.folder.Folder"
            class="installtool.factories.demo"
            content_factory_id="installtool.factories.demo"
            addform_class=".add.AddMixIn"
            schema=".interfaces.IDemo"
            for="*"
            view="calldemo.html"
            title="Demo"
            description="Demo Demo"
            permission="zope.ManageContent"
            >
            
            <property name="par1" value="11"/>
            <property name="par2" value="12"/>
            <property name="par3" value="13"/>
            <property name="par4" value="14"/>
            
        </factoryform>
    
    Параметры директивы factoryform::
        
        name -- имя фабрики (уникальное), фабрика
            создается как класс в модуле installtool.factories
            под этим именем,

        root -- корневой объект процедуры инсталляции: вначале
            создается и добавляется он, а затем все остальное.
        
        class -- полный путь к фабрике,
        
        content_factory_id -- указывается полное имя фабрики
        
        addform_class -- всегда .add.AddMixIn
        
        schema -- указывается схема для генерации формы,
        
        for -- указывается интерфейс, для которого отображается
            форма вызова фабрики,
        
        view -- имя формы добавления, нужно указывать обязательно,
        
        title -- название п. меню,
        
        description -- описание формы,
        
        permission -- разрешение для вызова формы и показа пункта меню.
